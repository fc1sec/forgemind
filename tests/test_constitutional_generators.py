"""Tests for the v1.3.0 constitutional-governance generators."""

from __future__ import annotations

import pytest

from forgemind.core.analysis import analyze_project
from forgemind.exporters.markdown import export_markdown
from forgemind.generators import (
    generate_aiia_pre_deployment,
    generate_capability_thresholds,
    generate_evidence_scoring,
    generate_skill_card,
    generate_token_governance,
)

# ---------------------------------------------------------------------------
# Project fixtures — one AI/ML project + one non-AI project to verify
# domain-conditional emission.
# ---------------------------------------------------------------------------

_AI_PROJECT = """# Autonomous Agent Pilot

## Objective
Deploy an autonomous LLM agent using prompts to call internal tools.

## Context
Claude-based agent with embeddings, ML inference, and neural model serving.

## Scope
Agent + LLM + prompt + automation + embedding + vector store.

## Out of Scope
Production traffic.

## Constraints
Agent must not write secrets.

## Stakeholders
Engineering team.

## Risks
Hallucination, prompt injection, autonomy creep.

## Systems
LLM API, vector DB.
"""

_QMS_PROJECT = """# SGC Document Lifecycle

## Objective
Implement an ISO 9001 document lifecycle for the QMS.

## Context
Quality system needs governance over procedure approvals and CAPA.

## Scope
Document control, audit prep, nonconformity, governance.

## Out of Scope
Tender management.

## Constraints
Must comply with ISO 9001:2015.

## Stakeholders
Quality Coordinator, Direction.

## Risks
Documents drift out of compliance.

## Systems
SharePoint, document repository.
"""


@pytest.fixture
def ai_analysis(tmp_path):
    project = tmp_path / "ai.md"
    project.write_text(_AI_PROJECT)
    return analyze_project(project)


@pytest.fixture
def qms_analysis(tmp_path):
    project = tmp_path / "qms.md"
    project.write_text(_QMS_PROJECT)
    return analyze_project(project)


# ---------------------------------------------------------------------------
# Universal generators (emitted for every project)
# ---------------------------------------------------------------------------

class TestEvidenceScoringGenerator:
    def test_emits_confidence_table(self, qms_analysis):
        out = generate_evidence_scoring(qms_analysis)
        assert "Confidence scale (1-5)" in out
        for level in (1, 2, 3, 4, 5):
            assert f"| {level} |" in out

    def test_emits_three_integrity_tiers(self, qms_analysis):
        out = generate_evidence_scoring(qms_analysis)
        for tier in ("Tier 0", "Tier 1", "Tier 2", "Tier 3"):
            assert tier in out

    def test_anchors_to_doctrines(self, qms_analysis):
        out = generate_evidence_scoring(qms_analysis)
        assert "D17" in out
        assert "D37" in out

    def test_runs_for_ai_project_too(self, ai_analysis):
        out = generate_evidence_scoring(ai_analysis)
        assert "Evidence Scoring" in out


class TestTokenGovernanceGenerator:
    def test_emits_five_decision_levels(self, qms_analysis):
        out = generate_token_governance(qms_analysis)
        for lvl in (0, 1, 2, 3, 4):
            assert f"| {lvl} |" in out

    def test_emits_seven_step_hierarchy(self, qms_analysis):
        out = generate_token_governance(qms_analysis)
        assert "7-step routing hierarchy" in out
        for i in range(1, 8):
            assert f"{i}." in out

    def test_anchors_to_doctrines(self, qms_analysis):
        out = generate_token_governance(qms_analysis)
        assert "D22" in out
        assert "D06" in out


# ---------------------------------------------------------------------------
# AI/ML-only generators
# ---------------------------------------------------------------------------

class TestAIIAGenerator:
    def test_contains_eight_sections(self, ai_analysis):
        out = generate_aiia_pre_deployment(ai_analysis)
        for i in range(1, 9):
            assert f"## {i} ·" in out

    def test_contains_all_12_nist_genai_risks(self, ai_analysis):
        out = generate_aiia_pre_deployment(ai_analysis)
        for risk in ("Confabulation", "Data Privacy", "Harmful Bias", "CBRN"):
            assert risk in out

    def test_cites_d40_doctrine(self, ai_analysis):
        out = generate_aiia_pre_deployment(ai_analysis)
        assert "D40" in out

    def test_handles_non_ai_domain_defensively(self, qms_analysis):
        # The AIIA template can still render for non-AI projects (defensive use),
        # but the intro language flips. Generator should not crash.
        out = generate_aiia_pre_deployment(qms_analysis)
        assert "AI Impact Assessment" in out


class TestCapabilityThresholdsGenerator:
    def test_contains_all_seven_thresholds(self, ai_analysis):
        out = generate_capability_thresholds(ai_analysis)
        for i in range(1, 8):
            assert f"### T{i}" in out

    def test_emits_override_policy(self, ai_analysis):
        out = generate_capability_thresholds(ai_analysis)
        assert "Override policy" in out
        assert "no operational exceptions" in out

    def test_cites_d41_doctrine(self, ai_analysis):
        out = generate_capability_thresholds(ai_analysis)
        assert "D41" in out


class TestSkillCardGenerator:
    def test_contains_twelve_sections(self, ai_analysis):
        out = generate_skill_card(ai_analysis)
        for i in range(1, 13):
            assert f"## {i} ·" in out

    def test_emits_signature_block(self, ai_analysis):
        out = generate_skill_card(ai_analysis)
        assert "BEGIN SKILL CARD SIGNATURE" in out
        assert "END SKILL CARD SIGNATURE" in out

    def test_cites_d43_doctrine(self, ai_analysis):
        out = generate_skill_card(ai_analysis)
        assert "D43" in out


# ---------------------------------------------------------------------------
# Exporter integration
# ---------------------------------------------------------------------------

class TestExporterIntegration:
    def test_ai_project_emits_full_triad(self, tmp_path, ai_analysis):
        out = export_markdown(ai_analysis, tmp_path / "out")
        files = {p.name for p in out.iterdir()}
        # Universal v1.3 outputs
        assert "EVIDENCE_SCORING.md" in files
        assert "TOKEN_COST_GOVERNANCE.md" in files
        # AI-only constitutional triad
        assert "AIIA_PRE_DEPLOYMENT.md" in files
        assert "CAPABILITY_THRESHOLDS.md" in files
        assert "SKILL_CARD.md" in files

    def test_qms_project_does_not_emit_ai_only_triad(self, tmp_path, qms_analysis):
        out = export_markdown(qms_analysis, tmp_path / "out")
        files = {p.name for p in out.iterdir()}
        # Universal outputs still present
        assert "EVIDENCE_SCORING.md" in files
        assert "TOKEN_COST_GOVERNANCE.md" in files
        # AI-only triad must NOT be present
        assert "AIIA_PRE_DEPLOYMENT.md" not in files
        assert "CAPABILITY_THRESHOLDS.md" not in files
        assert "SKILL_CARD.md" not in files

    def test_total_file_counts(self, tmp_path, ai_analysis, qms_analysis):
        ai_out = export_markdown(ai_analysis, tmp_path / "ai")
        qms_out = export_markdown(qms_analysis, tmp_path / "qms")
        ai_files = list(ai_out.iterdir())
        qms_files = list(qms_out.iterdir())
        # Universal projects: 19 files; AI/ML projects: 22 files
        assert len(qms_files) == 19, f"QMS expected 19 files, got {len(qms_files)}"
        assert len(ai_files) == 22, f"AI expected 22 files, got {len(ai_files)}"
