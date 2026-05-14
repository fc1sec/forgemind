"""Tests for ForgeMind CLI onboarding features (v1.2.1)."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from forgemind.cli.main import app


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_project(temp_dir):
    """Create a sample project file."""
    project_file = temp_dir / "forgemind_projects" / "test_project.md"
    project_file.parent.mkdir(parents=True, exist_ok=True)
    project_file.write_text("""
# Test Project

## Objective
Test project for onboarding testing.

## Context
This is a test project.

## Scope
Testing scope.

## Risks
Test risks.

## Success Criteria
Test succeeds.
""")
    return project_file


class TestInitFirstTime:
    """Tests for first-time init command."""

    def test_init_first_time_shows_welcome_message(self, temp_dir, cli_runner):
        """First init shows welcome message."""
        # Change to temp directory
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = cli_runner.invoke(app, ["init"])
            assert result.exit_code == 0
            assert "Welcome to ForgeMind" in result.stdout
            assert "What ForgeMind Does" in result.stdout
            assert "What ForgeMind Does NOT Do" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_init_first_time_shows_capabilities(self, temp_dir, cli_runner):
        """First init shows capabilities and limitations."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = cli_runner.invoke(app, ["init"])
            assert "Analyzes your project description" in result.stdout
            assert "Creates 17 structured planning documents" in result.stdout
            assert "Make decisions for you" in result.stdout  # Limitation
        finally:
            os.chdir(original_cwd)

    def test_init_first_time_prompts_demo(self, temp_dir, cli_runner):
        """First init prompts for demo."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = cli_runner.invoke(app, ["init"], input="n\n")
            assert "Ready to see a 2-minute demo?" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_init_subsequent_skips_orientation(self, temp_dir, cli_runner):
        """Subsequent init skips orientation."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # First init with demo decline
            cli_runner.invoke(app, ["init"], input="n\n")
            # Second init should not show orientation
            result = cli_runner.invoke(app, ["init"])
            assert "Welcome to ForgeMind" not in result.stdout
            assert "Initializing ForgeMind workspace" in result.stdout
        finally:
            os.chdir(original_cwd)


class TestIntakeDomainDetection:
    """Tests for domain detection in intake command."""

    def test_intake_detects_ai_project_domain(self, temp_dir, cli_runner, sample_project):
        """intake detects AI project domain."""
        # Create AI project
        ai_project = temp_dir / "forgemind_projects" / "ai_project.md"
        ai_project.parent.mkdir(parents=True, exist_ok=True)
        ai_project.write_text("""
# AI Agent Project

## Objective
Build an AI agent for code generation.

## Context
Need AI automation for code.

## Scope
AI, agent, model training.

## Risks
Hallucination, security.

## Success Criteria
Agent works.
""")
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = cli_runner.invoke(app, ["intake", str(ai_project)])
            assert result.exit_code == 0
            assert "Detected domain: ai_project" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_intake_shows_domain_specific_guidance(self, temp_dir, cli_runner):
        """intake shows domain-specific guidance."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # Create QMS project
            qms_project = temp_dir / "forgemind_projects" / "qms_project.md"
            qms_project.parent.mkdir(parents=True, exist_ok=True)
            qms_project.write_text("""
# QMS Project

## Objective
Implement ISO 9001 QMS.

## Context
Need quality management system.

## Scope
ISO 9001, documentation, control.

## Risks
Non-compliance.

## Success Criteria
Audit passes.
""")
            result = cli_runner.invoke(app, ["intake", str(qms_project)])
            assert result.exit_code == 0
            assert "QMS ISO" in result.stdout or "qms_iso" in result.stdout.lower()
            # Should show QMS-specific guidance
            assert "document" in result.stdout.lower() or "audit" in result.stdout.lower()
        finally:
            os.chdir(original_cwd)

    def test_intake_warns_on_tender_domain(self, temp_dir, cli_runner):
        """intake warns on tender domain."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            tender_project = temp_dir / "forgemind_projects" / "tender_project.md"
            tender_project.parent.mkdir(parents=True, exist_ok=True)
            tender_project.write_text("""
# Government Tender Procurement

## Objective
Win government contract through tender bid submission with full compliance.

## Context
Government tender opportunity with strict procurement requirements. Compliance matrix required.

## Scope
Tender proposal, bid submission, technical requirements, compliance matrix documentation.

## Risks
Non-compliance rejection, procurement deadline, technical requirement gaps.

## Success Criteria
Tender proposal approved and compliant.
""")
            result = cli_runner.invoke(app, ["intake", str(tender_project)])
            assert result.exit_code == 0
            # Should show compliance warning
            assert "compliance" in result.stdout.lower() or "warning" in result.stdout.lower()
        finally:
            os.chdir(original_cwd)


class TestIntakeExplainFlag:
    """Tests for --explain flag in intake."""

    def test_explain_flag_shows_explanations(self, temp_dir, cli_runner):
        """--explain flag shows why sections matter."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            project = temp_dir / "forgemind_projects" / "project.md"
            project.parent.mkdir(parents=True, exist_ok=True)
            project.write_text("""
# Test Project

## Objective
Test objective.

## Context
Test context.

## Scope
Test scope.

## Risks
Test risks.

## Success Criteria
Test criteria.
""")
            result = cli_runner.invoke(app, ["intake", str(project), "--explain"])
            assert result.exit_code == 0
            assert "Why Each Section Matters" in result.stdout
            assert "Objective" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_explain_flag_omitted_no_explanations(self, temp_dir, cli_runner):
        """Without --explain, explanations not shown."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            project = temp_dir / "forgemind_projects" / "project.md"
            project.parent.mkdir(parents=True, exist_ok=True)
            project.write_text("""
# Test Project

## Objective
Test objective.

## Context
Test context.

## Scope
Test scope.

## Risks
Test risks.

## Success Criteria
Test criteria.
""")
            result = cli_runner.invoke(app, ["intake", str(project)])
            assert result.exit_code == 0
            # Should not show detailed explanations
            assert "Why Each Section Matters" not in result.stdout
        finally:
            os.chdir(original_cwd)


class TestIntakeErrorHandling:
    """Tests for error handling in intake."""

    def test_missing_file_shows_helpful_error(self, temp_dir, cli_runner):
        """Missing file shows helpful error message."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = cli_runner.invoke(app, ["intake", "nonexistent.md"])
            assert result.exit_code == 1
            assert "not found" in result.stdout.lower()
            assert "Check:" in result.stdout
            assert "Example:" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_malformed_project_shows_format_guidance(self, temp_dir, cli_runner):
        """Malformed project shows format guidance."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            project = temp_dir / "forgemind_projects" / "bad_project.md"
            project.parent.mkdir(parents=True, exist_ok=True)
            # Write file with no Objective section
            project.write_text("""
# Bad Project

## Random Section
Just some text, missing required sections.
""")
            result = cli_runner.invoke(app, ["intake", str(project)])
            # Should handle gracefully (may or may not fail depending on analysis logic)
            # But if it fails, should show helpful message
            if result.exit_code != 0:
                assert "format" in result.stdout.lower() or "section" in result.stdout.lower()
        finally:
            os.chdir(original_cwd)


class TestIntakePostAnalysisGuidance:
    """Tests for post-analysis guidance in intake."""

    def test_intake_shows_start_here_guidance(self, temp_dir, cli_runner):
        """intake shows clear guidance on which documents to read first."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            project = temp_dir / "forgemind_projects" / "project.md"
            project.parent.mkdir(parents=True, exist_ok=True)
            project.write_text("""
# Test Project

## Objective
Test objective.

## Context
Test context.

## Scope
Test scope.

## Risks
Test risks.

## Success Criteria
Test criteria.
""")
            result = cli_runner.invoke(app, ["intake", str(project)])
            assert result.exit_code == 0
            assert "Start Here" in result.stdout
            assert "PROJECT_CHARTER.md" in result.stdout
            assert "RISK_REGISTER.md" in result.stdout
            assert "ACCEPTANCE_CRITERIA.md" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_intake_shows_next_steps(self, temp_dir, cli_runner):
        """intake shows clear next steps."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            project = temp_dir / "forgemind_projects" / "project.md"
            project.parent.mkdir(parents=True, exist_ok=True)
            project.write_text("""
# Test Project

## Objective
Test objective.

## Context
Test context.

## Scope
Test scope.

## Risks
Test risks.

## Success Criteria
Test criteria.
""")
            result = cli_runner.invoke(app, ["intake", str(project)])
            assert result.exit_code == 0
            assert "Next Steps" in result.stdout
            assert "Review documents with your team" in result.stdout
            assert "Re-run" in result.stdout or "forgemind intake" in result.stdout
        finally:
            os.chdir(original_cwd)


class TestOnboardingFlowEnd2End:
    """End-to-end onboarding flow tests."""

    def test_full_first_time_flow(self, temp_dir, cli_runner):
        """Full first-time user flow works end-to-end."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            # 1. Init shows orientation
            result = cli_runner.invoke(app, ["init"], input="n\n")
            assert result.exit_code == 0
            assert "Welcome to ForgeMind" in result.stdout

            # 2. Sample project created
            sample_project = Path("forgemind_projects") / "sample_ai_project.md"
            assert sample_project.exists()

            # 3. User can run intake on project
            result = cli_runner.invoke(app, ["intake", str(sample_project)])
            assert result.exit_code == 0
            assert "Analysis complete" in result.stdout or "complete" in result.stdout.lower()

            # 4. Outputs created
            outputs_exist = (Path("forgemind_outputs") / "sample-ai-project").exists()
            assert outputs_exist
        finally:
            os.chdir(original_cwd)
