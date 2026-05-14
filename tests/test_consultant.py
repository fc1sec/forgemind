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
        # Find the iso9001 option index
        iso_index = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_index)

        # iso9001 has exactly 1 variant — variant question should be skipped
        turn = session.next_turn()
        assert turn is not None
        assert turn.purpose == "Proceed confirmation"

        # Confirm
        session.answer(turn, 0)  # yes
        assert session.next_turn() is None
        assert session.outcome() == CalibrationOutcome.READY

    def test_disclosure_lists_variant_and_boundaries(self, qms_project: Path):
        session = ConsultantSession(qms_project)
        session.load_project()
        # Walk to confirmation
        turn = session.next_turn()
        session.answer(turn, 0)  # quality_management
        turn = session.next_turn()
        iso_index = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_index)

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
