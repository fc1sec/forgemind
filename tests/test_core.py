"""Test core engines."""

import pytest

from forgemind.core.analysis import analyze_project
from forgemind.core.classifier import classify_domain
from forgemind.core.intake import extract_project_slug, parse_markdown
from forgemind.core.rdmaicsi import generate_rdmaicsi_phases
from forgemind.core.senge import generate_senge_disciplines
from forgemind.schemas.project import ProjectInput


@pytest.fixture
def sample_project_file(tmp_path):
    """Create a sample project file."""
    project_content = """# Test Project

## Objective
Build a test system

## Context
Testing framework context

## Scope
Test scope definition

## Constraints
Time and budget constraints

## Risks
Identified risks list
"""
    project_file = tmp_path / "test_project.md"
    project_file.write_text(project_content)
    return str(project_file)


def test_intake_parsing(sample_project_file):
    """Test Markdown parsing."""
    project_input = parse_markdown(sample_project_file)
    assert "Build a test system" in project_input.objective
    assert "Testing framework context" in project_input.context


def test_intake_missing_sections(tmp_path):
    """Test graceful handling of missing sections."""
    project_file = tmp_path / "minimal.md"
    project_file.write_text("# Minimal Project\n\n## Objective\nOne thing")
    project_input = parse_markdown(str(project_file))
    assert "One thing" in project_input.objective
    assert project_input.scope == "Not evidenced in available input."


def test_project_slug_generation():
    """Test slug generation from filename."""
    slug = extract_project_slug("path/to/My Test Project.md")
    assert slug == "my-test-project"


def test_classifier_ai_project():
    """Test domain classification for AI projects."""
    project_input = ProjectInput(
        objective="Build an AI agent",
        context="Using Claude for automation",
        scope="Agent can execute tasks",
    )
    domain, is_detected = classify_domain(project_input)
    assert domain == "ai_project"
    assert is_detected is True


def test_classifier_software_project():
    """Test domain classification for software."""
    project_input = ProjectInput(
        objective="Build a new feature",
        context="Adding API endpoints",
        scope="Frontend and backend changes",
    )
    domain, is_detected = classify_domain(project_input)
    assert domain == "software_project"
    assert is_detected is True


def test_classifier_qms_project():
    """Test domain classification for QMS."""
    project_input = ProjectInput(
        objective="Implement document control",
        context="ISO 9001 compliance",
        scope="QMS improvements",
    )
    domain, is_detected = classify_domain(project_input)
    assert domain == "qms_iso"
    assert is_detected is True


def test_classifier_generic_fallback():
    """Test fallback to generic domain."""
    project_input = ProjectInput(
        objective="Do something",
        context="No keywords match",
        scope="Vague scope",
        constraints="Budget and schedule limits",
    )
    domain, is_detected = classify_domain(project_input)
    assert domain == "generic"
    assert is_detected is False


def test_rdmaicsi_phases():
    """Test RDMAICSI returns exactly 8 phases."""
    phases = generate_rdmaicsi_phases()
    assert len(phases) == 8

    # Check each phase
    phase_names = [p.phase for p in phases]
    expected = ["Recognize", "Define", "Measure", "Analyze", "Improve", "Control", "Standardize", "Integrate"]
    assert phase_names == expected

    # Check structure
    for phase in phases:
        assert phase.purpose
        assert phase.key_questions
        assert len(phase.key_questions) >= 3
        assert phase.required_evidence
        assert phase.expected_output
        assert phase.risk_if_skipped


def test_senge_disciplines():
    """Test Senge returns exactly 5 disciplines."""
    disciplines = generate_senge_disciplines()
    assert len(disciplines) == 5

    # Check names
    names = [d.discipline for d in disciplines]
    expected = [
        "Systems Thinking",
        "Mental Models",
        "Shared Vision",
        "Personal Mastery",
        "Team Learning",
    ]
    assert names == expected

    # Check structure
    for disc in disciplines:
        assert disc.purpose
        assert disc.diagnostic_questions
        assert len(disc.diagnostic_questions) >= 3
        assert disc.project_risk_if_ignored
        assert disc.recommended_practice


def test_analysis_complete(sample_project_file):
    """Test complete analysis workflow."""
    analysis = analyze_project(sample_project_file)

    # Check metadata
    assert analysis.metadata.name
    assert analysis.metadata.slug
    assert analysis.metadata.domain

    # Check all analyses present
    assert len(analysis.rdmaicsi_phases) == 8
    assert len(analysis.senge_disciplines) == 5
    assert len(analysis.risks) >= 3
    assert len(analysis.assumptions) >= 2
    assert len(analysis.acceptance_criteria) >= 1
    assert len(analysis.backlog) >= 1
    assert len(analysis.control_plan) >= 1
    assert len(analysis.decision_log) >= 1

    # Check maturity estimate exists
    assert analysis.maturity_estimate
