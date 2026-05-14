"""ForgeMind CLI using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from forgemind import __version__
from forgemind.cli.version import check_version_availability
from forgemind.core.analysis import analyze_project
from forgemind.exporters.json_exporter import export_json
from forgemind.exporters.markdown import export_markdown

app = typer.Typer(
    help="ForgeMind: MethodOps engine for AI-assisted project execution readiness"
)
console = Console()


def app_callback(
    skip_version_check: bool = typer.Option(
        False,
        "--skip-version-check",
        help="Skip version availability check (for testing or CI/CD)",
    )
) -> None:
    """App-level callback to check version before any command runs."""
    # Run version check non-blocking (will fail silently on network errors)
    check_version_availability(skip=skip_version_check)


# Register the callback with the app
app.callback(invoke_without_command=False)(app_callback)


@app.command()
def init() -> None:
    """Initialize ForgeMind workspace with sample project."""
    console.print("[bold cyan]Initializing ForgeMind workspace...[/bold cyan]")

    # Create directories
    Path("forgemind_projects").mkdir(exist_ok=True)
    Path("forgemind_outputs").mkdir(exist_ok=True)

    # Create sample project file
    sample_file = Path("forgemind_projects/sample_ai_project.md")
    sample_content = """# AI Backend Automation Project

## Objective
Develop an AI-powered agent that can autonomously build and deploy backend services based on specifications.

## Context
Our team spends significant time on routine backend setup. An AI agent could accelerate this 10x while ensuring consistency.

## Scope
- Agent can read service specification in Markdown
- Agent can generate boilerplate code (models, routes, tests)
- Agent can validate against patterns
- Agent submits PR for human review

## Out of Scope
- Database schema design (human-reviewed)
- Production deployment (human approval gate)
- Security fixes (human review required)

## Constraints
- Must work without external API calls
- Must use open models or local tools
- Must maintain audit trail of agent decisions
- Must not modify security-sensitive code

## Stakeholders
- Engineering Lead: accepts/reviews all agent PRs
- Security Team: reviews outputs for vulnerabilities
- Platform Team: integrates with CI/CD

## Current State
Manual backend setup takes 4-6 hours per service.

## Desired State
Agent generates 80% of boilerplate in <30 minutes, human review adds 1-2 hours.

## Risks
- Agent generates insecure code
- Agent hallucinates patterns
- Scope creeps to include dangerous operations

## Systems
- GitHub for version control
- Local Claude or similar for agent
- CI/CD pipeline for testing

## Success Criteria
- Generated code passes linter and tests
- Security review completes in <1 hour
- First 5 agents ships successfully

## Timeline
- Week 1: Define agent boundaries and test harness
- Week 2: Agent MVP and testing
- Week 3: Production pilot with monitoring
"""
    sample_file.write_text(sample_content)
    console.print(f"[green]✓[/green] Created {sample_file}")

    # Print next steps
    console.print()
    console.print("[bold cyan]Next steps:[/bold cyan]")
    console.print("[cyan]1. Edit or create a project file in forgemind_projects/[/cyan]")
    console.print("[cyan]2. Run: forgemind intake forgemind_projects/your_project.md[/cyan]")
    console.print("[cyan]3. Check forgemind_outputs/ for generated analyses[/cyan]")
    console.print()
    console.print("[dim]Example project created at:[/dim]")
    console.print(f"[cyan]{sample_file}[/cyan]")


@app.command()
def intake(project_file: str) -> None:
    """Analyze project and generate structured outputs."""
    console.print(f"[bold cyan]Analyzing project: {project_file}[/bold cyan]")

    try:
        # Analyze project
        analysis = analyze_project(project_file)

        # Create output directory
        output_dir = Path("forgemind_outputs") / analysis.metadata.slug
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export markdown outputs
        export_markdown(analysis, output_dir)

        # Print summary
        console.print()
        console.print("[green]✓[/green] [bold]Analysis complete![/bold]")
        console.print()
        console.print(f"[cyan]Project:[/cyan] {analysis.metadata.name}")
        console.print(f"[cyan]Domain:[/cyan] {analysis.metadata.domain}")
        console.print(f"[cyan]Maturity:[/cyan] {analysis.maturity_estimate}")
        console.print()
        console.print(f"[cyan]Outputs written to: {output_dir}[/cyan]")
        console.print()

        # List generated files
        console.print("[bold cyan]Generated files:[/bold cyan]")
        for file in sorted(output_dir.glob("*.md")):
            console.print(f"  [green]✓[/green] {file.name}")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def diagnose(project_file: str) -> None:
    """Quick diagnosis of project readiness."""
    console.print(f"[bold cyan]Diagnosing: {project_file}[/bold cyan]")

    try:
        analysis = analyze_project(project_file)

        # Create summary table
        table = Table(title="Project Readiness Diagnosis", show_header=True)
        table.add_column("Aspect", style="cyan")
        table.add_column("Status", style="green")

        table.add_row(
            "Project",
            analysis.metadata.name,
        )
        table.add_row(
            "Domain",
            f"{analysis.metadata.domain} {'(detected)' if analysis.metadata.detected_domain else '(explicit)'}",
        )
        table.add_row(
            "Maturity",
            analysis.maturity_estimate,
        )
        table.add_row(
            "Risks Identified",
            str(len(analysis.risks)),
        )
        table.add_row(
            "Assumptions",
            str(len(analysis.assumptions)),
        )
        table.add_row(
            "Acceptance Criteria",
            str(len(analysis.acceptance_criteria)),
        )
        table.add_row(
            "Backlog Items",
            str(len(analysis.backlog)),
        )

        console.print()
        console.print(table)

        # Top risks
        if analysis.risks:
            console.print()
            console.print("[bold cyan]Top Risks:[/bold cyan]")
            for risk in sorted(
                analysis.risks,
                key=lambda r: (r.get("severity") == "High", r.get("probability") == "High"),
                reverse=True,
            )[:3]:
                console.print(
                    f"  [red]⚠[/red]  {risk.get('risk', 'Unknown risk')}"
                )

        # Critical gaps
        critical_gaps = []
        if analysis.input.objective == "Not evidenced in available input.":
            critical_gaps.append("Objective not defined")
        if analysis.input.scope == "Not evidenced in available input.":
            critical_gaps.append("Scope not defined")
        if not analysis.acceptance_criteria:
            critical_gaps.append("Acceptance criteria missing")

        if critical_gaps:
            console.print()
            console.print("[bold yellow]Critical Gaps:[/bold yellow]")
            for gap in critical_gaps:
                console.print(f"  [yellow]→[/yellow]  {gap}")

        # Output location
        output_dir = Path("forgemind_outputs") / analysis.metadata.slug
        console.print()
        console.print(f"[cyan]Full analysis: {output_dir}[/cyan]")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def gate(project_file: str) -> None:
    """Check minimum readiness gates."""
    try:
        analysis = analyze_project(project_file)

        # Define gates
        gates = {
            "Objective defined": analysis.input.objective != "Not evidenced in available input.",
            "Context defined": analysis.input.context != "Not evidenced in available input.",
            "Scope defined": analysis.input.scope != "Not evidenced in available input.",
            "Risks generated": len(analysis.risks) > 0,
            "Assumptions generated": len(analysis.assumptions) > 0,
            "Acceptance criteria generated": len(analysis.acceptance_criteria) > 0,
            "Control plan exists": len(analysis.control_plan) > 0,
            "Human review gates": any(
                risk.get("human_review_required", False)
                for risk in analysis.risks
            ),
            "Outputs can be generated": True,
        }

        # Create gate table
        table = Table(title="Readiness Gates", show_header=True)
        table.add_column("Gate", style="cyan")
        table.add_column("Status", style="magenta")

        passed = 0
        for gate_name, status in gates.items():
            status_str = "[green]✓ Pass[/green]" if status else "[red]✗ Fail[/red]"
            table.add_row(gate_name, status_str)
            if status:
                passed += 1

        console.print()
        console.print(table)

        # Summary
        total = len(gates)
        console.print()
        console.print(f"[cyan]Gates passed: {passed}/{total}[/cyan]")

        # Determine readiness
        if passed == total:
            console.print()
            console.print("[green bold]✓ Project is READY for execution[/green bold]")
            raise typer.Exit(0)
        else:
            console.print()
            console.print(f"[yellow bold]⚠ {total - passed} gate(s) not yet passed[/yellow bold]")
            raise typer.Exit(1)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def handoff(
    project_file: str,
    target: str = typer.Option("generic-agent", help="Target agent: codex, claude-code, generic-agent"),
) -> None:
    """Generate agent-ready handoff document."""
    if target not in ["codex", "claude-code", "generic-agent"]:
        console.print(f"[red]Error:[/red] Unknown target: {target}")
        raise typer.Exit(1)

    try:
        analysis = analyze_project(project_file)

        # Create output directory
        output_dir = Path("forgemind_outputs") / analysis.metadata.slug
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate handoff (exported as part of markdown)
        export_markdown(analysis, output_dir)

        console.print()
        console.print(
            f"[green]✓[/green] Handoff generated for target: [cyan]{target}[/cyan]"
        )
        console.print(
            f"[cyan]{output_dir / 'AGENT_HANDOFF.md'}[/cyan]"
        )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def export(
    project_file: str,
    format: str = typer.Option("json", help="Export format: json or yaml"),
) -> None:
    """Export project analysis as JSON or YAML."""
    if format not in ["json", "yaml"]:
        console.print(f"[red]Error:[/red] Unknown format: {format}")
        raise typer.Exit(1)

    try:
        analysis = analyze_project(project_file)

        # Create output directory
        output_dir = Path("forgemind_outputs") / analysis.metadata.slug
        output_dir.mkdir(parents=True, exist_ok=True)

        if format == "json":
            output_file = export_json(analysis, output_dir)
            console.print(f"[green]✓[/green] Exported to: [cyan]{output_file}[/cyan]")
        else:
            console.print("[yellow]⚠ YAML export not yet implemented[/yellow]")
            console.print("[cyan]Use JSON export instead[/cyan]")
            raise typer.Exit(1)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version."""
    console.print(f"[cyan]ForgeMind[/cyan] v{__version__}")


if __name__ == "__main__":
    app()
