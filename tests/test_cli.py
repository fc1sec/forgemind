"""Test CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from forgemind.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help runs."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ForgeMind" in result.stdout


def test_version_command():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.stdout


def test_init_command(tmp_path):
    """Test init creates workspace."""
    # Change to temp directory
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["--skip-version-check", "init"])
        assert result.exit_code == 0
        assert Path("forgemind_projects").exists()
        assert Path("forgemind_outputs").exists()
        assert Path("forgemind_projects/sample_ai_project.md").exists()
    finally:
        os.chdir(original_cwd)


def test_intake_command(tmp_path):
    """Test intake generates all output files."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["--skip-version-check", "init"])

        result = runner.invoke(app, ["--skip-version-check", "intake", "forgemind_projects/sample_ai_project.md"])
        assert result.exit_code == 0

        # Check that output directory exists
        output_dir = Path("forgemind_outputs/sample-ai-project")
        assert output_dir.exists()

        # Check required files exist
        required_files = [
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
        ]

        for filename in required_files:
            assert (output_dir / filename).exists(), f"{filename} not generated"
    finally:
        os.chdir(original_cwd)


def test_diagnose_command(tmp_path):
    """Test diagnose prints summary."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["--skip-version-check", "init"])

        result = runner.invoke(app, ["--skip-version-check", "diagnose", "forgemind_projects/sample_ai_project.md"])
        assert result.exit_code == 0
        assert "Diagnosis" in result.stdout or "Project" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_gate_success(tmp_path):
    """Test gate passes for complete project."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["--skip-version-check", "init"])

        result = runner.invoke(app, ["--skip-version-check", "gate", "forgemind_projects/sample_ai_project.md"])
        # Sample project should be mostly complete
        assert result.exit_code == 0  # Should pass
    finally:
        os.chdir(original_cwd)


def test_gate_failure(tmp_path):
    """Test gate fails for incomplete project."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Create incomplete project
        Path("forgemind_projects").mkdir(parents=True, exist_ok=True)
        incomplete = Path("forgemind_projects/incomplete.md")
        incomplete.write_text("# Incomplete Project\n\n(No sections filled)")

        result = runner.invoke(app, ["--skip-version-check", "gate", "forgemind_projects/incomplete.md"])
        assert result.exit_code == 1  # Should fail
    finally:
        os.chdir(original_cwd)


def test_handoff_command(tmp_path):
    """Test handoff generation."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["--skip-version-check", "init"])

        result = runner.invoke(
            app,
            ["--skip-version-check", "handoff", "forgemind_projects/sample_ai_project.md", "--target", "codex"]
        )
        assert result.exit_code == 0
        assert "Handoff" in result.stdout or "AGENT_HANDOFF" in result.stdout
    finally:
        os.chdir(original_cwd)


def test_export_json(tmp_path):
    """Test JSON export."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        runner.invoke(app, ["--skip-version-check", "init"])

        result = runner.invoke(
            app,
            ["--skip-version-check", "export", "forgemind_projects/sample_ai_project.md", "--format", "json"]
        )
        assert result.exit_code == 0
        assert "json" in result.stdout.lower() or "exported" in result.stdout.lower()

        # Check JSON file exists
        assert Path("forgemind_outputs/sample-ai-project/sample-ai-project_analysis.json").exists()
    finally:
        os.chdir(original_cwd)
