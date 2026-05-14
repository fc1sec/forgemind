"""Tests for the ForgeMind consultant calibration session.

These tests drive the state machine deterministically (no interactive prompts)
to verify question flow, refusal protocol, and integration with the taxonomy.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from forgemind.cli.main import app
from forgemind.consultant import CalibrationOutcome, ConsultantSession

# ----------------------------------------------------------------------
# Fixtures — project markdown files for distinct disciplines
# ----------------------------------------------------------------------


def _write_project(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


@pytest.fixture
def qms_project(tmp_path: Path) -> Path:
    return _write_project(
        tmp_path,
        "qms.md",
        """# QMS Document Control Upgrade

## Objective
Implement ISO 9001:2015 document control for our quality management system.

## Context
We currently lack a structured QMS; documents drift without revision control.
We need audit-ready process documentation with full traceability.

## Scope
Document lifecycle, compliance, audit trail, nonconformity workflow.

## Constraints
Must align with ISO 9001:2015 §7.5 and §8.5.6.

## Risks
Non-compliance during certification audit; document drift; audit findings.

## Success Criteria
Pass external audit; all documents under revision control.
""",
    )


@pytest.fixture
def tender_project(tmp_path: Path) -> Path:
    return _write_project(
        tmp_path,
        "tender.md",
        """# Government Procurement Bid

## Objective
Submit a tender / bid for a government procurement opportunity.

## Context
Public procurement licitación with strict compliance matrix and RFI process.

## Scope
Tender proposal, bid submission, technical requirement compliance.

## Risks
Non-compliance rejection; tender deadline; partida budget overrun.

## Success Criteria
Tender awarded.
""",
    )


@pytest.fixture
def ai_project(tmp_path: Path) -> Path:
    return _write_project(
        tmp_path,
        "ai.md",
        """# Autonomous Agent for Code Generation

## Objective
Build an LLM-based autonomous agent that drafts backend code.

## Context
Manual scaffolding is slow; an AI agent could accelerate it 10x.

## Scope
Agent with tool permission matrix; human review gates; rollback plan.

## Risks
Hallucination; unsafe operations; scope creep.

## Success Criteria
Agent ships first 5 PRs successfully with no security regressions.
""",
    )


# ----------------------------------------------------------------------
# Session — happy path (ISO 9001 partial coverage, 1 variant)
# ----------------------------------------------------------------------


class TestSessionQMSHappyPath:
    """An ISO 9001 project: discipline → domain → (auto-skip variant) → confirm."""

    def test_load_classifies_to_qms(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        assert session.classifier_output == "qms_iso"
        # Discipline candidates include quality_management as the primary
        ids = [d.id for d in session.calibration.discipline_candidates]
        assert ids[0] == "quality_management"

    def test_full_dialog_reaches_ready(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()

        # Step 1: discipline → quality_management
        turn = session.next_turn()
        assert turn is not None
        assert turn.purpose == "Discipline calibration"
        session.answer(turn, 0)  # quality_management

        # Step 2: domain → iso9001
        turn = session.next_turn()
        assert turn is not None
        assert turn.purpose.startswith("Domain")
        iso_index = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_index)

        # Step 3: variant — iso9001 has 2 variants, so the question should fire
        turn = session.next_turn()
        assert turn is not None
        assert turn.purpose.startswith("Variant"), turn.purpose
        # Pick the production-validated CeSPI variant
        cespi_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "cespi_unlp_8state"
        )
        session.answer(turn, cespi_idx)

        # Step 4: confirm
        turn = session.next_turn()
        assert turn is not None
        assert turn.purpose == "Proceed confirmation"
        session.answer(turn, 0)  # yes
        assert session.next_turn() is None
        assert session.outcome() == CalibrationOutcome.READY

    def test_disclosure_lists_variant_and_boundaries(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        # discipline
        session.answer(session.next_turn(), 0)  # quality_management
        # domain → iso9001
        turn = session.next_turn()
        iso_index = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_index)
        # variant → cespi (now required because iso9001 has 2 variants)
        turn = session.next_turn()
        cespi_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "cespi_unlp_8state"
        )
        session.answer(turn, cespi_idx)

        disclosures = "\n".join(session.disclosures())
        assert "ISO 9001" in disclosures
        assert "partial" in disclosures.lower()
        assert "CeSPI" in disclosures or "8-state" in disclosures
        # At least one boundary condition should appear
        assert "Known gap" in disclosures


# ----------------------------------------------------------------------
# Refusal protocol — out-of-scope-by-design (tenders → legal_advice)
# ----------------------------------------------------------------------


class TestRefusalProtocol:
    """ForgeMind must refuse cleanly for out-of-scope projects."""

    def test_tender_project_refused_at_load_time(self, tender_project: Path):
        session = ConsultantSession(tender_project)
        session.load_project()
        assert session.calibration.refusal_reason is not None
        assert session.next_turn() is None
        assert session.outcome() == CalibrationOutcome.REFUSED

    def test_not_covered_domain_is_refused(self, qms_project: Path):
        """Choosing a not_covered domain (e.g. ISO 13485) refuses the session."""
        session = ConsultantSession(qms_project)
        session.load_project()
        # discipline → quality_management
        turn = session.next_turn()
        session.answer(turn, 0)
        # domain → iso13485 (not covered)
        turn = session.next_turn()
        idx = next(i for i, opt in enumerate(turn.options) if opt.value == "iso13485")
        session.answer(turn, idx)
        assert session.calibration.refusal_reason is not None
        assert session.outcome() == CalibrationOutcome.REFUSED

    def test_other_discipline_choice_refuses(self, qms_project: Path):
        """Picking '__other__' triggers refusal with guidance."""
        session = ConsultantSession(qms_project)
        session.load_project()
        turn = session.next_turn()
        other_idx = next(i for i, opt in enumerate(turn.options) if opt.value == "__other__")
        session.answer(turn, other_idx)
        assert session.calibration.refusal_reason is not None
        assert session.outcome() == CalibrationOutcome.REFUSED


# ----------------------------------------------------------------------
# Cancellation
# ----------------------------------------------------------------------


class TestCancellation:
    def test_user_can_cancel_at_confirmation(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        # discipline → quality_management
        session.answer(session.next_turn(), 0)
        # domain → iso9001
        turn = session.next_turn()
        idx = next(i for i, opt in enumerate(turn.options) if opt.value == "iso9001")
        session.answer(turn, idx)
        # variant → cespi (iso9001 has 2 variants now)
        turn = session.next_turn()
        cespi_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "cespi_unlp_8state"
        )
        session.answer(turn, cespi_idx)
        # confirm → no
        turn = session.next_turn()
        assert turn.purpose == "Proceed confirmation"
        no_idx = next(i for i, opt in enumerate(turn.options) if opt.value == "no")
        session.answer(turn, no_idx)
        assert session.outcome() == CalibrationOutcome.CANCELLED


# ----------------------------------------------------------------------
# Generic mode — user picks "none of the above" at domain step
# ----------------------------------------------------------------------


class TestGenericMode:
    def test_generic_mode_reaches_ready(self, ai_project: Path):
        session = ConsultantSession(ai_project)
        session.load_project()
        # Pick the first discipline candidate (likely ai_ml)
        session.answer(session.next_turn(), 0)
        # Pick __generic__ at the domain step
        turn = session.next_turn()
        generic_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "__generic__"
        )
        session.answer(turn, generic_idx)
        # Confirm → yes
        turn = session.next_turn()
        assert turn.purpose == "Proceed confirmation"
        session.answer(turn, 0)  # yes
        assert session.outcome() == CalibrationOutcome.READY


# ----------------------------------------------------------------------
# Error paths
# ----------------------------------------------------------------------


class TestErrors:
    def test_missing_file_raises(self, tmp_path: Path):
        session = ConsultantSession(tmp_path / "does_not_exist.md")
        with pytest.raises(FileNotFoundError):
            session.load_project()

    def test_invalid_answer_index_raises(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        turn = session.next_turn()
        with pytest.raises(ValueError):
            session.answer(turn, 999)


# ----------------------------------------------------------------------
# Variant pluralism — ISO 9001 now has 2 variants; user must choose
# ----------------------------------------------------------------------


class TestVariantPluralism:
    """Verify the consultant offers and records the user's variant choice."""

    def test_iso9001_offers_both_variants(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        # Walk to the variant step
        session.answer(session.next_turn(), 0)  # discipline
        turn = session.next_turn()  # domain
        iso_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_idx)
        # Variant turn must be present and offer both variants
        turn = session.next_turn()
        assert turn is not None and turn.purpose.startswith("Variant")
        values = {opt.value for opt in turn.options}
        assert "cespi_unlp_8state" in values
        assert "iso9001_minimalist_5state" in values

    def test_choosing_minimalist_variant_records_in_disclosure(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        session.answer(session.next_turn(), 0)  # discipline
        turn = session.next_turn()  # domain
        iso_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_idx)
        turn = session.next_turn()  # variant
        min_idx = next(
            i
            for i, opt in enumerate(turn.options)
            if opt.value == "iso9001_minimalist_5state"
        )
        session.answer(turn, min_idx)
        # Variant is recorded in calibration state
        assert session.calibration.variant is not None
        assert session.calibration.variant.id == "iso9001_minimalist_5state"
        # And reflected in disclosures
        text = "\n".join(session.disclosures())
        assert "Minimalist" in text or "5-state" in text

    def test_plugin_can_construct_with_each_variant(self):
        """The plugin itself supports both variants at the code level."""
        from forgemind.plugins.iso9001_pattern import ISO9001ReversePattern

        cespi = ISO9001ReversePattern(variant_id="cespi_unlp_8state")
        minimalist = ISO9001ReversePattern(variant_id="iso9001_minimalist_5state")
        # Distinct state machines
        cespi_states = {s.state_name for s in cespi.get_supported_states()}
        min_states = {s.state_name for s in minimalist.get_supported_states()}
        assert "Created" in cespi_states  # CeSPI-only state
        assert "In Force" in cespi_states  # CeSPI-only state
        assert "Created" not in min_states
        assert "In Force" not in min_states
        # Both share canonical states
        assert {"Draft", "Under Review", "Approved", "Signed", "Obsolete"} <= min_states
        assert {"Draft", "Under Review", "Approved", "Signed", "Obsolete"} <= cespi_states

    def test_plugin_default_variant_is_cespi(self):
        from forgemind.plugins.iso9001_pattern import ISO9001ReversePattern

        default = ISO9001ReversePattern()
        assert default.variant_id == "cespi_unlp_8state"

    def test_plugin_rejects_unknown_variant(self):
        from forgemind.plugins.iso9001_pattern import ISO9001ReversePattern

        with pytest.raises(ValueError):
            ISO9001ReversePattern(variant_id="not_a_real_variant")


# ----------------------------------------------------------------------
# Auditability — CONSULTANT_CALIBRATION.md is written when consult completes
# ----------------------------------------------------------------------


class TestVariantComparison:
    """Side-by-side variant comparison: CLI command + consultant inline option."""

    def test_compare_variants_command_lists_both(self):
        runner = CliRunner()
        result = runner.invoke(app, ["compare-variants", "iso9001"])
        assert result.exit_code == 0
        assert "CeSPI" in result.stdout
        assert "Minimalist" in result.stdout or "5-state" in result.stdout
        # Decision criteria for both variants must appear
        assert "Choose this if" in result.stdout
        assert result.stdout.lower().count("pros") >= 1
        assert result.stdout.lower().count("cons") >= 1

    def test_compare_variants_single_variant_domain_exits_zero(self):
        """A domain with only one variant should not pretend to compare."""
        runner = CliRunner()
        # ml_systems has one variant in the current taxonomy
        result = runner.invoke(app, ["compare-variants", "ml_systems"])
        assert result.exit_code == 0
        assert "only one variant" in result.stdout.lower()

    def test_compare_variants_unknown_domain_errors(self):
        runner = CliRunner()
        result = runner.invoke(app, ["compare-variants", "totally_made_up"])
        assert result.exit_code == 1

    def test_consultant_offers_compare_option_when_multiple_variants(
        self, qms_project: Path
    ):
        session = ConsultantSession(qms_project)
        session.load_project()
        session.answer(session.next_turn(), 0)  # discipline
        turn = session.next_turn()  # domain
        iso_idx = next(i for i, opt in enumerate(turn.options) if opt.value == "iso9001")
        session.answer(turn, iso_idx)
        # Variant question must include the compare option
        turn = session.next_turn()
        assert turn is not None and turn.purpose.startswith("Variant")
        values = {opt.value for opt in turn.options}
        assert "__compare__" in values

    def test_choosing_compare_yields_inline_comparison_and_repeats_variant_question(
        self, qms_project: Path
    ):
        session = ConsultantSession(qms_project)
        session.load_project()
        session.answer(session.next_turn(), 0)  # discipline
        turn = session.next_turn()  # domain
        iso_idx = next(i for i, opt in enumerate(turn.options) if opt.value == "iso9001")
        session.answer(turn, iso_idx)
        # Pick __compare__
        turn = session.next_turn()
        compare_idx = next(i for i, opt in enumerate(turn.options) if opt.value == "__compare__")
        session.answer(turn, compare_idx)
        # Comparison should be available
        assert session.calibration.comparison_requested is True
        text = "\n".join(session.render_variant_comparison())
        assert "CeSPI" in text and ("Minimalist" in text or "5-state" in text)
        assert "Choose this if" in text
        # Next turn must STILL be the variant question (user didn't pick yet)
        turn = session.next_turn()
        assert turn is not None and turn.purpose.startswith("Variant")

    def test_variant_has_decision_criteria_populated(self):
        """Schema integrity: every iso9001 variant must declare decision criteria."""
        from forgemind.disciplines import get_taxonomy

        tx = get_taxonomy()
        iso = tx.get_domain("iso9001")
        assert iso is not None
        for v in iso.variants:
            assert v.when_to_choose, f"{v.id} missing when_to_choose"
            assert v.pros, f"{v.id} missing pros"
            assert v.cons, f"{v.id} missing cons"


class TestCalibrationAuditFile:
    def test_calibration_log_written_to_output_dir(
        self, qms_project: Path, tmp_path: Path
    ):
        runner = CliRunner()
        out_dir = tmp_path / "outputs"
        result = runner.invoke(
            app,
            [
                "consult",
                str(qms_project),
                "--auto-accept",
                "--output-dir",
                str(out_dir),
            ],
        )
        assert result.exit_code == 0, result.stdout
        log = out_dir / "CONSULTANT_CALIBRATION.md"
        assert log.exists(), "CONSULTANT_CALIBRATION.md must be written by consult"
        content = log.read_text(encoding="utf-8")
        # Records the calibration choices
        assert "Quality Management Systems" in content
        assert "ISO 9001" in content
        # And the variant
        assert "cespi_unlp_8state" in content or "CeSPI" in content
        # And the escalation contact
        assert "Escalate to" in content


# ----------------------------------------------------------------------
# CLI integration
# ----------------------------------------------------------------------


class TestConsultCommand:
    """End-to-end CLI smoke tests for `forgemind consult`."""

    def test_consult_auto_accept_qms(self, qms_project: Path, tmp_path: Path):
        runner = CliRunner()
        out_dir = tmp_path / "outputs"
        result = runner.invoke(
            app,
            [
                "consult",
                str(qms_project),
                "--auto-accept",
                "--output-dir",
                str(out_dir),
            ],
        )
        assert result.exit_code == 0, result.stdout
        assert "Calibration complete" in result.stdout
        assert "Outputs written" in result.stdout
        # Outputs were actually written
        assert (out_dir / "PROJECT_CHARTER.md").exists()

    def test_consult_refuses_tender(self, tender_project: Path):
        runner = CliRunner()
        result = runner.invoke(app, ["consult", str(tender_project), "--auto-accept"])
        # Exit code 2 == refused
        assert result.exit_code == 2
        assert "cannot advise" in result.stdout.lower() or "refused" in result.stdout.lower()

    def test_consult_missing_file(self, tmp_path: Path):
        runner = CliRunner()
        result = runner.invoke(app, ["consult", str(tmp_path / "nope.md"), "--auto-accept"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
