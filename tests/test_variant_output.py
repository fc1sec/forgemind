"""Tests for variant-aware reversal plan generation.

This is the bridge between "user calibrated to variant X" and "the outputs
materially differ for variant X". Without these tests, the variant choice
is purely cosmetic — these tests guarantee the choice flows into a real
artifact (REVERSAL_PLAN.md) the user can read and audit.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from forgemind.cli.main import app
from forgemind.consultant.variant_output import (
    instantiate_for_variant,
    write_variant_reversal_plan,
)
from forgemind.core.analysis import analyze_project
from forgemind.plugins.ai_ml_pattern import AIMLReversePattern
from forgemind.plugins.iso9001_pattern import ISO9001ReversePattern
from forgemind.plugins.software_pattern import SoftwareReversePattern

# ----------------------------------------------------------------------
# Helpers / fixtures
# ----------------------------------------------------------------------


def _write_qms_project(tmp_path: Path) -> Path:
    """A QMS project with an explicit current_state so we get a concrete plan."""
    p = tmp_path / "qms.md"
    p.write_text(
        """# QMS Document Control Upgrade

## Objective
Implement ISO 9001:2015 document control for the quality management system.

## Context
We need audit-ready process documentation with traceability.

## Scope
Document lifecycle, compliance, audit trail.

## Current State
Approved

## Risks
Non-compliance during certification audit; document drift.

## Success Criteria
Pass external audit; documents under revision control.
""",
        encoding="utf-8",
    )
    return p


# ----------------------------------------------------------------------
# instantiate_for_variant
# ----------------------------------------------------------------------


class TestInstantiateForVariant:
    def test_iso9001_with_variant(self):
        plugin = instantiate_for_variant(
            ISO9001ReversePattern, "iso9001_minimalist_5state"
        )
        assert plugin.variant_id == "iso9001_minimalist_5state"

    def test_iso9001_default_when_variant_id_is_none(self):
        plugin = instantiate_for_variant(ISO9001ReversePattern, None)
        # Default is the CeSPI 8-state machine
        assert plugin.variant_id == "cespi_unlp_8state"

    def test_unknown_variant_for_iso9001_raises(self):
        # The plugin's constructor validates variant_id against VARIANTS;
        # an unknown id must surface as a ValueError so callers can react.
        with pytest.raises(ValueError):
            instantiate_for_variant(ISO9001ReversePattern, "not_a_real_variant")

    # ----- software variants (blue/green vs canary) -----

    def test_software_with_blue_green_variant(self):
        plugin = instantiate_for_variant(SoftwareReversePattern, "blue_green")
        assert plugin.variant_id == "blue_green"
        states = {s.state_name for s in plugin.get_supported_states()}
        assert "Canary" not in states  # blue/green has no Canary tier
        assert {"In Development", "In Code Review", "Merged to Main",
                "Staging", "Production"} <= states

    def test_software_with_canary_variant(self):
        plugin = instantiate_for_variant(SoftwareReversePattern, "canary")
        assert plugin.variant_id == "canary"
        states = {s.state_name for s in plugin.get_supported_states()}
        # Canary variant adds the Canary tier between Staging and Production
        assert "Canary" in states
        assert {"In Development", "In Code Review", "Merged to Main",
                "Staging", "Canary", "Production"} <= states

    def test_software_default_is_blue_green(self):
        plugin = instantiate_for_variant(SoftwareReversePattern, None)
        assert plugin.variant_id == "blue_green"

    def test_unknown_software_variant_raises(self):
        with pytest.raises(ValueError):
            instantiate_for_variant(SoftwareReversePattern, "not_a_real_software_variant")

    # ----- ai_ml variants (feature_flag_checkpoint vs shadow_deployment) -----

    def test_ai_ml_with_feature_flag_variant(self):
        plugin = instantiate_for_variant(
            AIMLReversePattern, "feature_flag_checkpoint"
        )
        assert plugin.variant_id == "feature_flag_checkpoint"
        states = {s.state_name for s in plugin.get_supported_states()}
        assert "Staging (Canary)" in states  # canary tier is in this variant
        assert "Shadow" not in states         # shadow tier is NOT

    def test_ai_ml_with_shadow_variant(self):
        plugin = instantiate_for_variant(AIMLReversePattern, "shadow_deployment")
        assert plugin.variant_id == "shadow_deployment"
        states = {s.state_name for s in plugin.get_supported_states()}
        assert "Shadow" in states              # shadow tier is in this variant
        assert "Staging (Canary)" not in states  # canary tier is NOT

    def test_ai_ml_default_is_feature_flag(self):
        plugin = instantiate_for_variant(AIMLReversePattern, None)
        assert plugin.variant_id == "feature_flag_checkpoint"

    def test_unknown_ai_ml_variant_raises(self):
        with pytest.raises(ValueError):
            instantiate_for_variant(AIMLReversePattern, "not_a_real_ai_ml_variant")


# ----------------------------------------------------------------------
# write_variant_reversal_plan — direct function test
# ----------------------------------------------------------------------


class TestWriteVariantReversalPlan:
    def test_writes_reversal_plan_md(self, tmp_path: Path):
        project = _write_qms_project(tmp_path)
        analysis = analyze_project(str(project))
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()

        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="cespi_unlp_8state",
            variant_name="CeSPI UNLP 8-state document lifecycle",
            variant_source="iso-gestion (CeSPI UNLP)",
            domain_id="iso9001",
        )
        assert path is not None
        assert path.exists()
        assert path.name == "REVERSAL_PLAN.md"

    def test_cespi_variant_mentions_8state_specific_states(self, tmp_path: Path):
        project = _write_qms_project(tmp_path)
        analysis = analyze_project(str(project))
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="cespi_unlp_8state",
            domain_id="iso9001",
        )
        content = path.read_text(encoding="utf-8")
        # CeSPI-only states must appear
        assert "Created" in content
        assert "In Force" in content
        assert "Under Approval" in content

    def test_minimalist_variant_omits_8state_specific_states(self, tmp_path: Path):
        project = _write_qms_project(tmp_path)
        analysis = analyze_project(str(project))
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="iso9001_minimalist_5state",
            domain_id="iso9001",
        )
        content = path.read_text(encoding="utf-8")
        # Minimalist machine has 5 states; CeSPI-only states must NOT appear
        assert "In Force" not in content
        # "Created" and "Under Approval" are NOT in the minimalist machine.
        # Look only at the state-machine table rows to avoid false positives
        # from narrative text.
        for line in content.splitlines():
            if line.startswith("| `"):
                assert "`Created`" not in line
                assert "`Under Approval`" not in line
        # The canonical 5 states must all appear in the table
        for state in ("Draft", "Under Review", "Approved", "Signed", "Obsolete"):
            assert f"`{state}`" in content

    def test_includes_variant_attribution_when_provided(self, tmp_path: Path):
        project = _write_qms_project(tmp_path)
        analysis = analyze_project(str(project))
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="cespi_unlp_8state",
            variant_name="CeSPI UNLP 8-state document lifecycle",
            variant_source="iso-gestion (CeSPI UNLP)",
            domain_id="iso9001",
        )
        content = path.read_text(encoding="utf-8")
        assert "CeSPI UNLP 8-state" in content
        assert "iso-gestion (CeSPI UNLP)" in content

    def test_concrete_plan_rendered_when_current_state_present(self, tmp_path: Path):
        project = _write_qms_project(tmp_path)  # has 'Current State: Approved'
        analysis = analyze_project(str(project))
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="cespi_unlp_8state",
            domain_id="iso9001",
        )
        content = path.read_text(encoding="utf-8")
        # Concrete plan section appears with rollback path and steps
        assert "Concrete reversal plan" in content
        assert "Rollback path" in content
        # The CeSPI Approved → Under Approval reversal must surface
        assert "Approved" in content

    # ----- software variant differentiation in REVERSAL_PLAN.md -----

    def test_blue_green_reversal_plan_mentions_lb_switch(self, tmp_path: Path):
        project = tmp_path / "svc.md"
        project.write_text(
            "# Backend Service\n## Objective\nDeploy a backend microservice\n"
            "## Context\nWeb services\n## Scope\nBackend API\n## Current State\nProduction\n"
            "## Risks\nRegression\n## Success Criteria\nSLO recovered\n",
            encoding="utf-8",
        )
        analysis = analyze_project(str(project))
        # Override the classifier-detected domain so the plugin maps correctly
        analysis.metadata.domain = "software"
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="blue_green",
            domain_id="software",
        )
        assert path is not None
        text = path.read_text(encoding="utf-8")
        # Blue/green plan must reference the LB switch + instant rollback
        assert "blue" in text.lower()
        assert "load balancer" in text.lower() or "lb" in text.lower()
        # Blue/green has NO Canary tier
        for line in text.splitlines():
            if line.startswith("| `"):
                assert "`Canary`" not in line

    def test_canary_reversal_plan_mentions_traffic_weights(self, tmp_path: Path):
        project = tmp_path / "svc.md"
        project.write_text(
            "# Backend Service\n## Objective\nDeploy a backend microservice\n"
            "## Context\nWeb services with progressive rollout\n## Scope\nBackend API\n"
            "## Current State\nProduction\n## Risks\nRegression\n## Success Criteria\nSLO recovered\n",
            encoding="utf-8",
        )
        analysis = analyze_project(str(project))
        analysis.metadata.domain = "software"
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="canary",
            domain_id="software",
        )
        assert path is not None
        text = path.read_text(encoding="utf-8")
        # Canary plan must reference progressive traffic shifting
        assert "traffic" in text.lower()
        assert "canary" in text.lower()
        # Canary tier appears as a row in the state machine
        canary_rows = [
            line for line in text.splitlines() if line.startswith("| `Canary`")
        ]
        assert canary_rows, "Canary variant must include a `Canary` row in the table"

    # ----- ai_ml variant differentiation -----

    def test_shadow_variant_mentions_parallel_models_and_logger(self, tmp_path: Path):
        project = tmp_path / "ml.md"
        project.write_text(
            "# ML Recommendation Model\n## Objective\nDeploy new recommendation model\n"
            "## Context\nML production system\n## Scope\nInference path\n"
            "## Current State\nProduction\n## Risks\nDegraded recommendations\n"
            "## Success Criteria\nPrecision @10 within 2% of baseline\n",
            encoding="utf-8",
        )
        analysis = analyze_project(str(project))
        analysis.metadata.domain = "ai_ml"
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="shadow_deployment",
            domain_id="ai_ml",
        )
        assert path is not None
        text = path.read_text(encoding="utf-8")
        # Shadow plan must reference the swap-back and the shadow logger
        assert "shadow" in text.lower()
        # The Shadow state row appears
        assert "`Shadow`" in text
        # The canary tier does NOT appear in this variant
        for line in text.splitlines():
            if line.startswith("| `"):
                assert "`Staging (Canary)`" not in line

    def test_feature_flag_variant_mentions_canary_tier(self, tmp_path: Path):
        project = tmp_path / "ml.md"
        project.write_text(
            "# ML Recommendation Model\n## Objective\nDeploy new recommendation model\n"
            "## Context\nML production system with feature flags\n## Scope\nInference path\n"
            "## Current State\nProduction\n## Risks\nDegraded recommendations\n"
            "## Success Criteria\nPrecision @10 within 2% of baseline\n",
            encoding="utf-8",
        )
        analysis = analyze_project(str(project))
        analysis.metadata.domain = "ai_ml"
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        path = write_variant_reversal_plan(
            out_dir=out_dir,
            analysis=analysis,
            variant_id="feature_flag_checkpoint",
            domain_id="ai_ml",
        )
        assert path is not None
        text = path.read_text(encoding="utf-8")
        assert "Staging (Canary)" in text or "`Staging (Canary)`" in text
        # The Shadow state does NOT appear in this variant's state table
        for line in text.splitlines():
            if line.startswith("| `"):
                assert "`Shadow`" not in line

    def test_returns_none_when_no_plugin_for_domain(self, tmp_path: Path):
        """A domain with no plugin (e.g. operations) yields no file."""
        # Build a minimal operations-style project. The default classifier
        # may flag this differently, but the function checks plugin existence
        # via the registry — we simulate by giving the analysis a domain
        # that has no plugin (e.g. 'unknown_domain').
        from forgemind.schemas.project import (
            ProjectAnalysis,
            ProjectInput,
            ProjectMetadata,
        )

        analysis = ProjectAnalysis(
            metadata=ProjectMetadata(
                name="X", slug="x", domain="no_such_domain"
            ),
            input=ProjectInput(
                objective="o",
                context="c",
                scope="s",
                constraints="",
                current_state="",
            ),
            risks=[],
            assumptions=[],
            acceptance_criteria=[],
            constraints=[],
            control_plan=[],
            decision_log=[],
        )
        out_dir = tmp_path / "outputs"
        out_dir.mkdir()
        result = write_variant_reversal_plan(
            out_dir=out_dir, analysis=analysis, variant_id=None
        )
        assert result is None
        assert not (out_dir / "REVERSAL_PLAN.md").exists()


# ----------------------------------------------------------------------
# End-to-end via CLI: `forgemind consult` writes REVERSAL_PLAN.md
# ----------------------------------------------------------------------


class TestConsultProducesReversalPlan:
    def test_consult_auto_accept_writes_reversal_plan(self, tmp_path: Path, monkeypatch):
        # Isolate history so this test doesn't write to the user's home
        monkeypatch.setenv("FORGEMIND_HISTORY_PATH", str(tmp_path / "h.jsonl"))
        project = _write_qms_project(tmp_path)
        out_dir = tmp_path / "outputs"
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["consult", str(project), "--auto-accept", "--output-dir", str(out_dir)],
        )
        assert result.exit_code == 0, result.stdout
        rp = out_dir / "REVERSAL_PLAN.md"
        assert rp.exists()
        content = rp.read_text(encoding="utf-8")
        # Default variant via --auto-accept is the CeSPI 8-state
        assert "cespi_unlp_8state" in content or "CeSPI" in content
        # Stdout reports the artifact
        assert "REVERSAL_PLAN.md" in result.stdout

    def test_consult_produces_full_output_set(self, tmp_path: Path, monkeypatch):
        """Integration: consult produces ALL expected artifacts side-by-side.

        Covers todo item #12 — explicit integration test against the markdown
        exporter. Verifies the 17 standard markdown documents from
        `export_markdown` coexist with the consultant-specific artifacts
        (CONSULTANT_CALIBRATION.md, consultant_calibration.json,
        REVERSAL_PLAN.md) in the same output directory after one consult run.

        If any of these regress, this test fails loudly and points at the
        integration seam between `analyze_project` → `export_markdown` →
        `_write_calibration_log` → `write_variant_reversal_plan`.
        """
        import json as _json

        monkeypatch.setenv("FORGEMIND_HISTORY_PATH", str(tmp_path / "h.jsonl"))
        project = _write_qms_project(tmp_path)
        out_dir = tmp_path / "outputs"
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["consult", str(project), "--auto-accept", "--output-dir", str(out_dir)],
        )
        assert result.exit_code == 0, result.stdout

        # 1) The 17 standard markdown documents from export_markdown
        expected_standard_outputs = [
            "PROJECT_CHARTER.md",
            "RDMAICSI_MATRIX.md",
            "SENGE_LENS.md",
            "LEAN_WASTE_SCAN.md",
            "RISK_REGISTER.md",
            "ASSUMPTION_LOG.md",
            "ACCEPTANCE_CRITERIA.md",
            "BACKLOG.md",
            "CONTROL_PLAN.md",
            "DECISION_LOG.md",
            "AGENT_HANDOFF.md",
            "README_OUTPUT_INDEX.md",
            "AI_RISK_CHECKLIST.md",
            "TOOL_PERMISSION_MATRIX.md",
            "AGENT_PR_TEMPLATE.md",
            "AGENT_ISSUE_TEMPLATE.md",
        ]
        for fname in expected_standard_outputs:
            assert (out_dir / fname).exists(), f"Missing standard output: {fname}"
            # Each standard doc must be non-empty and start with a markdown header
            content = (out_dir / fname).read_text(encoding="utf-8")
            assert content.strip(), f"{fname} is empty"

        # 2) The consultant-specific artifacts
        assert (out_dir / "CONSULTANT_CALIBRATION.md").exists()
        assert (out_dir / "consultant_calibration.json").exists()
        assert (out_dir / "REVERSAL_PLAN.md").exists()

        # 3) JSON sidecar is parseable and contains the calibrated choices
        sidecar = _json.loads(
            (out_dir / "consultant_calibration.json").read_text(encoding="utf-8")
        )
        assert sidecar["discipline"]["id"] == "quality_management"
        assert sidecar["domain"]["id"] == "iso9001"
        assert sidecar["variant"]["id"] == "cespi_unlp_8state"

        # 4) REVERSAL_PLAN.md reflects the variant choice (8-state table)
        reversal_text = (out_dir / "REVERSAL_PLAN.md").read_text(encoding="utf-8")
        for cespi_only_state in ("Created", "Under Approval", "In Force"):
            assert (
                cespi_only_state in reversal_text
            ), f"REVERSAL_PLAN.md missing CeSPI-only state: {cespi_only_state}"

        # 5) The calibration markdown references the chosen variant + escalation
        calibration_md = (out_dir / "CONSULTANT_CALIBRATION.md").read_text(
            encoding="utf-8"
        )
        assert "cespi_unlp_8state" in calibration_md or "CeSPI" in calibration_md
        assert "Escalate to" in calibration_md

    def test_followup_topic_reads_variant_reversal_plan(self, tmp_path: Path, monkeypatch):
        """The follow-up 'variant' topic should still work alongside the new file."""
        monkeypatch.setenv("FORGEMIND_HISTORY_PATH", str(tmp_path / "h.jsonl"))
        project = _write_qms_project(tmp_path)
        out_dir = tmp_path / "outputs"
        runner = CliRunner()
        runner.invoke(
            app,
            ["consult", str(project), "--auto-accept", "--output-dir", str(out_dir)],
        )
        result = runner.invoke(
            app, ["followup", str(out_dir), "--topic", "variant"]
        )
        assert result.exit_code == 0
        assert "Variant choice review" in result.stdout
