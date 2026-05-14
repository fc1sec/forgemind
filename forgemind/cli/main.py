"""ForgeMind CLI using Typer."""

from pathlib import Path
from typing import Optional

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


def _write_calibration_log(log_path: Path, session) -> None:
    """Persist a calibration audit log next to the generated outputs.

    Two files are written side by side:
      - CONSULTANT_CALIBRATION.md   — human-readable narrative
      - consultant_calibration.json — machine-readable sidecar consumed by
                                       `forgemind followup`

    Auditability is part of the consultant contract: a reviewer must be able to
    answer "what did ForgeMind calibrate to?" without re-running the session,
    and the follow-up command must be able to resume without re-prompting.
    """
    import json

    c = session.calibration
    payload = {
        "project_file": str(session.project_file),
        "taxonomy_version": session.taxonomy.version,
        "taxonomy_last_updated": session.taxonomy.last_updated,
        "discipline": {
            "id": c.discipline.id,
            "name": c.discipline.name,
        } if c.discipline else None,
        "domain": {
            "id": c.domain.id,
            "name": c.domain.name,
            "coverage": c.domain.coverage.value,
            "confidence": c.domain.confidence,
            "boundary_conditions": list(c.domain.boundary_conditions),
            "escalate_to": c.domain.escalate_to,
        } if c.domain else None,
        "variant": {
            "id": c.variant.id,
            "name": c.variant.name,
            "source": c.variant.source,
            "url": c.variant.url,
            "confidence": c.variant.confidence,
            "production_validated": c.variant.production_validated,
            "when_to_choose": list(c.variant.when_to_choose),
            "pros": list(c.variant.pros),
            "cons": list(c.variant.cons),
        } if c.variant else None,
    }
    json_sidecar = log_path.parent / "consultant_calibration.json"
    json_sidecar.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Consultant Calibration Log",
        "",
        f"- Project file: `{session.project_file}`",
        f"- Taxonomy version: {session.taxonomy.version}",
        f"- Taxonomy last updated: {session.taxonomy.last_updated}",
        "",
        "## Calibration choices",
        "",
    ]
    if c.discipline:
        lines.append(f"- **Discipline**: {c.discipline.name} (`{c.discipline.id}`)")
    if c.domain:
        cov = c.domain.coverage.value
        conf = (
            f", confidence {c.domain.confidence:.0%}"
            if c.domain.confidence is not None
            else ""
        )
        lines.append(f"- **Domain**: {c.domain.name} (`{c.domain.id}`) — {cov}{conf}")
    if c.variant:
        lines.append(f"- **Variant**: {c.variant.name} (`{c.variant.id}`)")
        if c.variant.source:
            lines.append(f"  - Source: {c.variant.source}")
        if c.variant.url:
            lines.append(f"  - URL: {c.variant.url}")
        lines.append(f"  - Confidence: {c.variant.confidence:.0%}")
        if c.variant.production_validated:
            since = f" since {c.variant.since}" if c.variant.since else ""
            lines.append(f"  - Production-validated{since}")
    if c.domain and c.domain.boundary_conditions:
        lines.append("")
        lines.append("## Known gaps disclosed at calibration time")
        lines.append("")
        for bc in c.domain.boundary_conditions:
            lines.append(f"- {bc}")
    if c.domain and c.domain.escalate_to:
        lines.append("")
        lines.append("## Escalate to")
        lines.append("")
        lines.append(c.domain.escalate_to)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "Outputs were generated under the assumptions above. Re-run "
        "`forgemind consult` if the project context changes materially."
    )
    log_path.write_text("\n".join(lines), encoding="utf-8")


@app.command()
def consult(
    project_file: str = typer.Argument(..., help="Path to the project markdown file"),
    auto_accept: bool = typer.Option(
        False,
        "--auto-accept",
        help="Skip prompts; pick defaults (suitable for CI / scripts)",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output-dir",
        help="Override the default output directory",
    ),
) -> None:
    """Run a calibrated consultant session before generating outputs.

    Unlike `intake`, which produces 17 documents directly, `consult` first
    asks calibrated questions to confirm:
      - which discipline applies,
      - which domain within it,
      - which validated variant (if more than one),
      - whether to proceed under disclosed coverage and boundary conditions.

    Use `--auto-accept` in non-interactive contexts to take all defaults.
    """
    try:
        from forgemind.consultant import CalibrationOutcome, ConsultantSession
    except ImportError as exc:
        console.print(f"[red]✗ Consultant module unavailable:[/red] {exc}")
        raise typer.Exit(1) from exc

    project_path = Path(project_file)
    if not project_path.exists():
        console.print(f"[red]✗ Project file not found:[/red] {project_path}")
        raise typer.Exit(1)

    session = ConsultantSession(project_path)

    console.print(
        f"[bold cyan]ForgeMind Consultant[/bold cyan] "
        f"[dim](taxonomy v{session.taxonomy.version})[/dim]\n"
    )

    # Step 1: load project + classify
    console.print("[bold]Reading project...[/bold]")
    try:
        session.load_project()
    except FileNotFoundError as exc:
        console.print(f"[red]✗ {exc}[/red]")
        raise typer.Exit(1) from exc

    if session.classifier_output:
        console.print(
            f"  Keyword classifier suggests: [cyan]{session.classifier_output}[/cyan]"
        )

    # If load_project already produced a refusal (e.g. tenders → out of scope),
    # bail out before asking any questions.
    if session.calibration.refusal_reason:
        console.print("\n[bold red]ForgeMind cannot advise on this project.[/bold red]")
        console.print(session.calibration.refusal_reason)
        raise typer.Exit(2)

    console.print()

    # Dialog loop
    while True:
        turn = session.next_turn()
        if turn is None:
            break

        console.print(
            f"[bold]Step {turn.step}/{turn.total_steps} — {turn.purpose}[/bold]"
        )
        console.print(turn.question)
        for line in turn.render_options():
            console.print(line)

        if auto_accept:
            choice = turn.default_index or 0
            console.print(
                f"  [dim]> {choice + 1} (auto-accept default)[/dim]"
            )
        else:
            default_display = (
                (turn.default_index + 1) if turn.default_index is not None else 1
            )
            try:
                raw = typer.prompt(
                    "  Your choice",
                    default=str(default_display),
                    show_default=True,
                )
            except (EOFError, typer.Abort, Exception):
                # Non-interactive (e.g. piped input exhausted): cancel cleanly.
                console.print("\n[yellow]Input unavailable — cancelling session.[/yellow]")
                raise typer.Exit(2) from None
            try:
                choice = int(raw) - 1
            except ValueError:
                console.print(f"[red]Invalid input '{raw}'; expected a number.[/red]")
                raise typer.Exit(1) from None

        try:
            session.answer(turn, choice)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

        # If the answer triggered a refusal, break early.
        if session.calibration.refusal_reason:
            break

        # If the user asked for a variant comparison, render it inline and
        # loop back to ask the variant question again. In --auto-accept mode
        # the comparison was never offered as the default, so this won't fire.
        if getattr(session.calibration, "comparison_requested", False):
            console.print()
            for line in session.render_variant_comparison():
                console.print(line)

        console.print()

    # Disclose what we calibrated to
    console.print("[bold]Calibration summary:[/bold]")
    for line in session.disclosures():
        console.print(f"  {line}")
    console.print()

    outcome = session.outcome()

    if outcome == CalibrationOutcome.REFUSED:
        console.print("[bold red]ForgeMind refused this session.[/bold red]")
        raise typer.Exit(2)

    if outcome == CalibrationOutcome.CANCELLED:
        console.print("[yellow]Session cancelled by user. No outputs generated.[/yellow]")
        raise typer.Exit(0)

    # READY → delegate to the same pipeline `intake` uses.
    console.print(
        "[bold cyan]Calibration complete. Generating outputs...[/bold cyan]"
    )
    try:
        analysis = analyze_project(str(project_path))
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]✗ Analysis failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    out_dir = Path(output_dir) if output_dir else Path("forgemind_outputs") / analysis.metadata.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    export_markdown(analysis, out_dir)

    # Persist the calibration log alongside the generated outputs so a
    # reviewer can always answer "what did the consultant calibrate to?".
    _write_calibration_log(out_dir / "CONSULTANT_CALIBRATION.md", session)

    console.print(f"[green]✓[/green] Outputs written to {out_dir}")
    console.print(
        "[dim]Outputs are STOCHASTIC — verify with the escalation contact "
        "above before relying on them for high-stakes decisions.[/dim]"
    )


@app.command()
def capabilities(
    discipline: Optional[str] = typer.Option(
        None, "--discipline", help="Filter to a single discipline id"
    ),
) -> None:
    """Show what ForgeMind can advise on (and what it knows it cannot).

    This is ForgeMind's self-knowledge: a coverage report across every
    discipline and domain, sourced from `forgemind/data/disciplines.yaml`.
    """
    try:
        from forgemind.disciplines import Coverage, get_taxonomy

        taxonomy = get_taxonomy()
    except (FileNotFoundError, ValueError, ImportError) as exc:
        console.print(f"[red]✗ Could not load disciplines taxonomy:[/red] {exc}")
        raise typer.Exit(1) from exc

    summary = taxonomy.summary()
    console.print(
        f"[bold cyan]ForgeMind Capabilities[/bold cyan] "
        f"(taxonomy v{taxonomy.version}, updated {taxonomy.last_updated})"
    )
    console.print(
        f"[dim]{summary['disciplines']} disciplines · "
        f"{summary['domains_total']} domains · "
        f"{summary['covered']} covered · "
        f"{summary['partial']} partial · "
        f"{summary['not_covered']} not covered · "
        f"{summary['out_of_scope_by_design']} out-of-scope by design[/dim]\n"
    )

    disciplines_iter = (
        [taxonomy.get_discipline(discipline)] if discipline else taxonomy.disciplines.values()
    )
    disciplines_iter = [d for d in disciplines_iter if d is not None]
    if not disciplines_iter:
        console.print(f"[red]✗ Unknown discipline:[/red] {discipline}")
        raise typer.Exit(1)

    coverage_styles = {
        Coverage.COVERED: ("[green]✓ covered[/green]", "green"),
        Coverage.PARTIAL: ("[yellow]◐ partial[/yellow]", "yellow"),
        Coverage.NOT_COVERED: ("[red]✗ not covered[/red]", "red"),
    }

    for disc in disciplines_iter:
        console.print(f"[bold]{disc.name}[/bold] [dim]({disc.id})[/dim]")
        if disc.description:
            console.print(f"  [dim]{disc.description}[/dim]")
        table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
        table.add_column("Domain", style="cyan", no_wrap=False)
        table.add_column("Coverage", no_wrap=True)
        table.add_column("Confidence", no_wrap=True)
        table.add_column("Escalate to", no_wrap=False)
        for domain in disc.domains.values():
            label, _ = coverage_styles[domain.coverage]
            conf = (
                f"{domain.confidence:.0%}"
                if domain.confidence is not None
                else "—"
            )
            table.add_row(
                domain.name,
                label,
                conf,
                domain.escalate_to or "—",
            )
        console.print(table)
        console.print()

    if not discipline:
        out_of_scope = taxonomy.list_out_of_scope()
        if out_of_scope:
            console.print("[bold red]Out of scope by design[/bold red] [dim](will always escalate)[/dim]")
            for entry in out_of_scope:
                console.print(f"  [red]✗[/red] [bold]{entry.id}[/bold] — {entry.reason}")
                console.print(f"      [dim]Escalate to: {entry.escalate_to}[/dim]")
            console.print()


@app.command()
def followup(
    output_dir: str = typer.Argument(..., help="Directory produced by `forgemind consult`"),
    auto_accept: bool = typer.Option(
        False,
        "--auto-accept",
        help="Exit immediately without entering the menu (CI / scripting)",
    ),
    topic: Optional[str] = typer.Option(
        None,
        "--topic",
        help="Render one specific topic and exit (variant|risks|acceptance|escalation)",
    ),
) -> None:
    """Revisit specific decisions in depth after a consult session.

    Loads the calibration sidecar written by `forgemind consult` and lets you
    drill into the variant choice, the risk register, acceptance criteria, or
    the escalation path without re-running analysis.
    """
    try:
        from forgemind.consultant import FollowupSession
    except ImportError as exc:
        console.print(f"[red]✗ Follow-up module unavailable:[/red] {exc}")
        raise typer.Exit(1) from exc

    out_path = Path(output_dir)
    if not out_path.exists():
        console.print(f"[red]✗ Output directory not found:[/red] {out_path}")
        raise typer.Exit(1)

    session = FollowupSession(out_path)
    try:
        session.load()
    except FileNotFoundError as exc:
        console.print(f"[red]✗ {exc}[/red]")
        raise typer.Exit(1) from exc

    console.print(
        "[bold cyan]ForgeMind Follow-up[/bold cyan] "
        f"[dim](output: {out_path})[/dim]\n"
    )

    # Single-topic mode (-t flag): render and exit.
    if topic is not None:
        valid_keys = {t.key for t in session.topics}
        if topic not in valid_keys:
            console.print(
                f"[red]✗ Unknown topic '{topic}'. Known: {sorted(valid_keys)}[/red]"
            )
            raise typer.Exit(1)
        for line in session.render_topic(topic):
            console.print(line)
        return

    # Auto-accept mode: print menu and exit cleanly (CI-friendly).
    if auto_accept:
        for line in session.menu_lines():
            console.print(line)
        console.print(
            "\n[dim]--auto-accept: exiting without entering the menu. "
            "Use --topic <key> to render a single topic, or omit --auto-accept "
            "for interactive mode.[/dim]"
        )
        return

    # Interactive menu loop.
    while True:
        for line in session.menu_lines():
            console.print(line)
        try:
            raw = typer.prompt(
                "Your choice", default=str(len(session.topics) + 1), show_default=True
            )
        except (EOFError, typer.Abort, Exception):
            console.print("\n[yellow]Input unavailable — exiting.[/yellow]")
            return
        try:
            choice = int(raw) - 1
        except ValueError:
            console.print(f"[red]Invalid input '{raw}'; expected a number.[/red]")
            continue

        if session.is_done_choice(choice):
            console.print("[green]Done.[/green]")
            return

        chosen_topic = session.topic_for_choice(choice)
        if chosen_topic is None:
            console.print("[red]Out-of-range choice.[/red]")
            continue

        console.print()
        for line in session.render_topic(chosen_topic.key):
            console.print(line)
        console.print()


@app.command("compare-variants")
def compare_variants(domain: str) -> None:
    """Compare the validated variants ForgeMind knows for a given domain.

    Use this BEFORE choosing a variant in `forgemind consult`. The output is
    a side-by-side decision support card: when to choose each variant, what
    you gain, what you give up.
    """
    try:
        from forgemind.disciplines import get_taxonomy

        taxonomy = get_taxonomy()
    except (FileNotFoundError, ValueError, ImportError) as exc:
        console.print(f"[red]✗ Could not load disciplines taxonomy:[/red] {exc}")
        raise typer.Exit(1) from exc

    target = taxonomy.get_domain(domain)
    if target is None:
        console.print(f"[red]✗ Unknown domain:[/red] {domain}")
        console.print("\nRun [cyan]forgemind capabilities[/cyan] to see known domains.")
        raise typer.Exit(1)

    if len(target.variants) < 2:
        console.print(
            f"[yellow]Only one variant declared for {target.name} — nothing to compare.[/yellow]"
        )
        if target.variants:
            v = target.variants[0]
            console.print(f"  - {v.name} ({v.id}), confidence {v.confidence:.0%}")
        raise typer.Exit(0)

    console.print(
        f"[bold cyan]Variant comparison for {target.name}[/bold cyan] "
        f"[dim]({target.id})[/dim]\n"
    )

    for variant in target.variants:
        console.print(f"[bold]{variant.name}[/bold] [dim]({variant.id})[/dim]")
        prod = " · production-validated" if variant.production_validated else ""
        console.print(f"  Confidence: {variant.confidence:.0%}{prod}")
        if variant.source:
            console.print(f"  Source: {variant.source}")

        if variant.when_to_choose:
            console.print("  [bold]Choose this if:[/bold]")
            for criterion in variant.when_to_choose:
                console.print(f"    • {criterion}")
        else:
            console.print("  [dim]Decision criteria not documented for this variant.[/dim]")

        if variant.pros:
            console.print("  [green]Pros:[/green]")
            for p in variant.pros:
                console.print(f"    [green]+[/green] {p}")
        if variant.cons:
            console.print("  [yellow]Cons:[/yellow]")
            for c in variant.cons:
                console.print(f"    [yellow]-[/yellow] {c}")
        console.print()

    console.print(
        "[dim]Tip: run `forgemind consult <project.md>` to be guided through "
        "variant selection in context.[/dim]"
    )


@app.command("explain-limits")
def explain_limits(domain: str) -> None:
    """Explain what ForgeMind does NOT cover for a given domain.

    Use this BEFORE relying on ForgeMind's advice in regulated, high-stakes,
    or unfamiliar domains. Honest disclosure of limitations is the contract
    of a responsible consultant.
    """
    try:
        from forgemind.disciplines import Coverage, get_taxonomy

        taxonomy = get_taxonomy()
    except (FileNotFoundError, ValueError, ImportError) as exc:
        console.print(f"[red]✗ Could not load disciplines taxonomy:[/red] {exc}")
        raise typer.Exit(1) from exc

    # Out-of-scope-by-design check first
    if domain in taxonomy.out_of_scope:
        entry = taxonomy.out_of_scope[domain]
        console.print(
            f"[bold red]Out of scope by design:[/bold red] [bold]{entry.id}[/bold]\n"
        )
        console.print(f"[bold]Why:[/bold] {entry.reason}")
        console.print(f"[bold]Rationale:[/bold] {entry.rationale}")
        console.print(f"[bold]Escalate to:[/bold] {entry.escalate_to}")
        return

    target = taxonomy.get_domain(domain)
    if target is None:
        console.print(f"[red]✗ Unknown domain:[/red] {domain}")
        console.print(
            "\nRun [cyan]forgemind capabilities[/cyan] to see all known domains."
        )
        raise typer.Exit(1)

    coverage_label = {
        Coverage.COVERED: "[green]Covered[/green]",
        Coverage.PARTIAL: "[yellow]Partial coverage[/yellow]",
        Coverage.NOT_COVERED: "[red]Not covered[/red]",
    }[target.coverage]

    console.print(f"[bold]{target.name}[/bold] [dim]({target.id})[/dim]")
    console.print(f"Status: {coverage_label}")
    if target.confidence is not None:
        console.print(f"Confidence: {target.confidence:.0%}")
    if target.escalate_to:
        console.print(f"Escalate to: {target.escalate_to}")
    console.print()

    if target.coverage == Coverage.NOT_COVERED:
        console.print("[bold red]ForgeMind will refuse to advise in this domain.[/bold red]")
        if target.reason:
            console.print(f"\n[bold]Reason:[/bold] {target.reason}")
        return

    if target.variants:
        console.print("[bold]Validated variants ForgeMind knows about:[/bold]")
        for variant in target.variants:
            console.print(f"  [green]✓[/green] [bold]{variant.name}[/bold] [dim]({variant.id})[/dim]")
            if variant.source:
                console.print(f"      Source: {variant.source}")
            if variant.url:
                console.print(f"      URL: {variant.url}")
            if variant.production_validated:
                since = f" since {variant.since}" if variant.since else ""
                console.print(f"      [dim]Production-validated{since}[/dim]")
            console.print(f"      Confidence: {variant.confidence:.0%}")
        console.print()

    if target.boundary_conditions:
        console.print("[bold]Known gaps / what ForgeMind does NOT cover here:[/bold]")
        for cond in target.boundary_conditions:
            console.print(f"  [yellow]⚠[/yellow]  {cond}")
        console.print()

    console.print(
        "[dim]Tip: even within covered domains, outputs are STOCHASTIC and require "
        "expert review for high-stakes decisions.[/dim]"
    )


if __name__ == "__main__":
    app()
