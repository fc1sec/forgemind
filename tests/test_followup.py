"""Tests for the ForgeMind follow-up consultant session.

Follow-up operates on a directory produced by `forgemind consult` and lets
the user drill into specific decisions (variant, risks, acceptance, escalation)
without re-running analysis. These tests verify:
  - The JSON sidecar written by consult is parseable by FollowupSession
  - Each topic renders meaningful content
  - The CLI command supports --topic (single render) and --auto-accept (CI)
  - Missing or malformed sidecars produce useful errors
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from forgemind.cli.main import app
from forgemind.consultant import FollowupSession, LoadedCalibration

# ----------------------------------------------------------------------
# Shared fixture: produce a real consult output directory we can follow-up on
# ----------------------------------------------------------------------


@pytest.fixture
def consult_output_dir(tmp_path: Path) -> Path:
    """Run `forgemind consult --auto-accept` on a QMS project; return out_dir."""
    project = tmp_path / "qms.md"
    project.write_text(
        """# QMS Document Control Upgrade

## Objective
Implement ISO 9001:2015 document control.

## Context
We need audit-ready process documentation with traceability.

## Scope
Document lifecycle, compliance, audit trail.

## Risks
Non-compliance during certification audit; document drift.

## Success Criteria
Pass external audit; documents under revision control.
""",
        encoding="utf-8",
    )
    out_dir = tmp_path / "outputs"
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["consult", str(project), "--auto-accept", "--output-dir", str(out_dir)],
    )
    assert result.exit_code == 0, result.stdout
    return out_dir


# ----------------------------------------------------------------------
# Sidecar round-trip
# ----------------------------------------------------------------------


class TestCalibrationSidecar:
    def test_consult_writes_json_sidecar(self, consult_output_dir: Path):
        sidecar = consult_output_dir / "consultant_calibration.json"
        assert sidecar.exists(), "consult must write consultant_calibration.json"
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        # Discipline + domain + variant must round-trip
        assert payload["discipline"]["id"] == "quality_management"
        assert payload["domain"]["id"] == "iso9001"
        assert payload["variant"]["id"] == "cespi_unlp_8state"
        # Boundary conditions and pros/cons preserved
        assert payload["domain"]["boundary_conditions"]
        assert payload["variant"]["pros"]
        assert payload["variant"]["cons"]

    def test_loaded_calibration_parses_sidecar(self, consult_output_dir: Path):
        loaded = LoadedCalibration.from_json(
            consult_output_dir / "consultant_calibration.json"
        )
        assert loaded.discipline["id"] == "quality_management"
        assert loaded.domain["id"] == "iso9001"
        assert loaded.variant["id"] == "cespi_unlp_8state"

    def test_missing_sidecar_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            LoadedCalibration.from_json(tmp_path / "consultant_calibration.json")


# ----------------------------------------------------------------------
# Topic rendering
# ----------------------------------------------------------------------


class TestTopicRendering:
    def test_variant_topic_includes_when_to_choose_and_cons(
        self, consult_output_dir: Path
    ):
        s = FollowupSession(consult_output_dir)
        s.load()
        text = "\n".join(s.render_topic("variant"))
        # Variant id + name
        assert "cespi_unlp_8state" in text or "CeSPI" in text
        # Pros and cons sections rendered
        assert "Pros" in text
        assert "Cons" in text or "gaps" in text.lower()
        # When-to-choose criteria
        assert "fit your context" in text.lower() or "reasons" in text.lower()

    def test_risks_topic_returns_risk_register_content(self, consult_output_dir: Path):
        s = FollowupSession(consult_output_dir)
        s.load()
        text = "\n".join(s.render_topic("risks"))
        # The risk register file is read and embedded
        assert "RISK_REGISTER" in text or "Risk" in text or "risk" in text

    def test_acceptance_topic_returns_acceptance_criteria(
        self, consult_output_dir: Path
    ):
        s = FollowupSession(consult_output_dir)
        s.load()
        text = "\n".join(s.render_topic("acceptance"))
        assert "Acceptance" in text or "acceptance" in text

    def test_escalation_topic_names_contact(self, consult_output_dir: Path):
        s = FollowupSession(consult_output_dir)
        s.load()
        text = "\n".join(s.render_topic("escalation"))
        # The QMS domain's escalation contact mentions ISO / QMS / auditor
        assert "ISO" in text or "QMS" in text or "auditor" in text.lower()
        # And the STOCHASTIC reminder is present
        assert "STOCHASTIC" in text or "expert" in text.lower()

    def test_unknown_topic_returns_placeholder(self, consult_output_dir: Path):
        s = FollowupSession(consult_output_dir)
        s.load()
        text = "\n".join(s.render_topic("not_a_real_topic"))
        assert "No renderer" in text


# ----------------------------------------------------------------------
# CLI command
# ----------------------------------------------------------------------


class TestFollowupCommand:
    def test_followup_auto_accept_prints_menu_and_exits(
        self, consult_output_dir: Path
    ):
        runner = CliRunner()
        result = runner.invoke(app, ["followup", str(consult_output_dir), "--auto-accept"])
        assert result.exit_code == 0
        assert "Follow-up" in result.stdout
        assert "Review the variant choice" in result.stdout

    def test_followup_single_topic_variant(self, consult_output_dir: Path):
        runner = CliRunner()
        result = runner.invoke(
            app, ["followup", str(consult_output_dir), "--topic", "variant"]
        )
        assert result.exit_code == 0
        assert "Variant choice review" in result.stdout
        assert "CeSPI" in result.stdout or "cespi_unlp_8state" in result.stdout

    def test_followup_single_topic_escalation(self, consult_output_dir: Path):
        runner = CliRunner()
        result = runner.invoke(
            app, ["followup", str(consult_output_dir), "--topic", "escalation"]
        )
        assert result.exit_code == 0
        assert "Escalation path" in result.stdout

    def test_followup_invalid_topic_errors(self, consult_output_dir: Path):
        runner = CliRunner()
        result = runner.invoke(
            app, ["followup", str(consult_output_dir), "--topic", "made_up"]
        )
        assert result.exit_code == 1
        assert "Unknown topic" in result.stdout

    def test_followup_missing_output_dir_errors(self, tmp_path: Path):
        runner = CliRunner()
        result = runner.invoke(
            app, ["followup", str(tmp_path / "does_not_exist"), "--auto-accept"]
        )
        assert result.exit_code == 1

    def test_followup_dir_without_sidecar_errors(self, tmp_path: Path):
        # A directory that exists but was not produced by consult
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        runner = CliRunner()
        result = runner.invoke(app, ["followup", str(empty_dir), "--auto-accept"])
        assert result.exit_code == 1
        assert "calibration" in result.stdout.lower() or "sidecar" in result.stdout.lower()
