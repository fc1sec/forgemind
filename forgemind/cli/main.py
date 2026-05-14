"""ForgeMind CLI using Typer."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from forgemind import __version__
from forgemind.core.analysis import analyze_project
from forgemind.core.classifier import classify_domain
from forgemind.exporters.json_exporter import export_json
from forgemind.exporters.markdown import export_markdown

app = typer.Typer(
    help="ForgeMind: MethodOps engine for AI-assisted project execution readiness"
)
console = Console()


@app.command()
def init() -> None:
    """Initialize ForgeMind workspace with sample project."""

    # Detect if this is first-time use
    projects_path = Path("forgemind_projects")
    is_first_time = not projects_path.exists()

    console.print("[bold cyan]Initializing ForgeMind workspace...[/bold cyan]")

    # Create directories
    projects_path.mkdir(exist_ok=True)
    Path("forgemind_outputs").mkdir(exist_ok=True)

    # Show orientation on first-time initialization
    if is_first_time:
        console.print()
        console.print("[bold cyan]Welcome to ForgeMind[/bold cyan]")
        console.print(
            "ForgeMind helps you structure projects [bold]before[/bold] you build them.\n"
            "In 15 minutes, you'll understand what ForgeMind does—and what it doesn't.\n"
        )

        # Show capabilities and limitations
        console.print("[bold]What ForgeMind Does[/bold]")
        console.print("  ✅ Analyzes your project description")
        console.print("  ✅ Creates 17 structured planning documents")
        console.print("  ✅ Helps surface risks, assumptions, gaps")
        console.print("  ✅ Prepares handoff context for AI agents\n")

        console.print("[bold]What ForgeMind Does NOT Do[/bold]")
        console.print("  ❌ Make decisions for you")
        console.print("  ❌ Know your domain better than you")
        console.print("  ❌ Guarantee your project succeeds")
        console.print("  ❌ Write code or deploy systems")
        console.print("  ❌ Certify compliance\n")

        # Prompt for demo (gracefully handle non-interactive environments
        # such as CI/CD where stdin is closed, which raises EOFError on
        # Python 3.10+ or Abort from click in some configurations).
        wants_demo = False
        try:
            wants_demo = typer.confirm(
                "Ready to see a 2-minute demo?", default=True
            )
        except Exception:
            # Non-interactive mode (EOFError, Abort, etc.):
            # skip demo prompt and continue
            wants_demo = False
        if wants_demo:
            console.print()
            console.print("[cyan]Next: Run the demo analysis[/cyan]")
            console.print("[cyan]forgemind intake forgemind_projects/sample_ai_project.md[/cyan]")
            console.print()

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
def intake(
    project_file: str,
    explain: bool = typer.Option(
        False,
        "--explain",
        help="Explain why each project section matters"
    ),
) -> None:
    """Analyze project and generate structured outputs."""
    console.print(f"[bold cyan]Analyzing project: {project_file}[/bold cyan]")

    try:
        # Check file exists first
        project_path = Path(project_file)
        if not project_path.exists():
            console.print("[red]✗ Project file not found[/red]")
            console.print(f"[dim]Looking for: {project_path.resolve()}[/dim]\n")
            console.print("[bold]Check:[/bold]")
            console.print("  1. File path is correct")
            console.print("  2. File is Markdown format (.md)")
            console.print("  3. File is in current directory or use full path\n")
            console.print("[cyan]Example:[/cyan] forgemind intake ./my_project.md")
            raise typer.Exit(1)

        # Analyze project
        analysis = analyze_project(project_file)

        # Domain detection
        domain, is_detected = classify_domain(analysis.input)
        console.print(f"[cyan]Detected domain:[/cyan] {domain}")

        # Show domain-specific guidance
        domain_guidance = {
            "ai_project": "ForgeMind helps you surface safety risks, model versioning strategies, and agent handoff context.",
            "software_project": "ForgeMind helps you identify architectural risks, deployment reversibility, and integration points.",
            "qms_iso": "ForgeMind helps you structure document lifecycle, approval gates, and audit trails.",
            "operations": "ForgeMind helps you map process flows, control points, and escalation procedures.",
            "odoo_erp": "ForgeMind helps you plan ERP configuration, data migration, and user adoption.",
            "tenders": "[yellow]⚠️  Tender analysis requires compliance expertise.[/yellow] ForgeMind structures planning but cannot certify regulatory compliance.",
            "generic": "ForgeMind helps you identify risks and success criteria.",
        }

        if domain in domain_guidance:
            console.print(f"[bold]{domain.upper().replace('_', ' ')} Analysis[/bold]")
            console.print(domain_guidance[domain] + "\n")

        # Show section explanations if requested
        if explain:
            console.print("[bold cyan]Why Each Section Matters[/bold cyan]")
            console.print("  [bold]Objective[/bold] — One-sentence project goal. Why: Keeps team aligned.")
            console.print("  [bold]Context[/bold] — Background and problem statement. Why: Helps stakeholders understand importance.")
            console.print("  [bold]Scope[/bold] — What's IN scope vs OUT of scope. Why: Prevents scope creep.")
            console.print("  [bold]Constraints[/bold] — Timeline, budget, team limits. Why: Forces realistic planning.")
            console.print("  [bold]Risks[/bold] — What could go wrong. Why: Plan mitigations now, not during crisis.")
            console.print("  [bold]Success Criteria[/bold] — How you'll know you succeeded. Why: Makes completion testable.\n")

        # Create output directory
        output_dir = Path("forgemind_outputs") / analysis.metadata.slug
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export markdown outputs
        export_markdown(analysis, output_dir)

        # Print summary
        console.print()
        console.print("[green]✓[/green] [bold]Analysis complete![/bold]")
        console.print()
        console.print("[bold cyan]Start Here[/bold cyan]")
        console.print("  1. [bold]PROJECT_CHARTER.md[/bold] — Objective, scope, success criteria")
        console.print("  2. [bold]RISK_REGISTER.md[/bold] — What could go wrong and how to mitigate")
        console.print("  3. [bold]ACCEPTANCE_CRITERIA.md[/bold] — How you'll know you succeeded\n")

        console.print("[bold cyan]Next Steps[/bold cyan]")
        console.print("  • Review documents with your team")
        console.print("  • Update your project based on what ForgeMind surfaced")
        console.print(f"  • Re-run: [cyan]forgemind intake {project_file}[/cyan] (takes ~2 seconds)\n")

        # Compliance warning for tenders
        if domain == "tenders":
            console.print(
                "[yellow]⚠️  Compliance Note[/yellow]\n"
                "For government tenders, validate ForgeMind outputs with legal/compliance team.\n"
                "ForgeMind structures planning but cannot guarantee regulatory compliance.\n"
            )

        console.print(f"[dim]Full analysis: {output_dir}[/dim]")

    except FileNotFoundError as e:
        console.print(f"[red]✗ File error:[/red] {e}")
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Check project format: [cyan]docs/FIRST_TIME_USER_GUIDE.md[/cyan] (Step 4)")
        console.print("  2. Ensure all required sections present (Objective, Context, Scope)")
        console.print("  3. Re-run: [cyan]forgemind intake your_project.md[/cyan]\n")
        console.print("[cyan]Still stuck?[/cyan] Report at github.com/forgemind/issues")
        raise typer.Exit(1)

    except Exception as e:
        console.print("[red]✗ Analysis failed[/red]")
        console.print(f"[dim]Error: {str(e)}[/dim]\n")
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Check project format: [cyan]docs/FIRST_TIME_USER_GUIDE.md[/cyan] (Step 4)")
        console.print("  2. Ensure all required sections present (Objective, Context, Scope)")
        console.print("  3. Re-run: [cyan]forgemind intake your_project.md[/cyan]\n")
        console.print("[cyan]Still stuck?[/cyan] Report at github.com/forgemind/issues")
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
