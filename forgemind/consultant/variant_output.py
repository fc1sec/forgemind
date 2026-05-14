"""Variant-aware output generation for the consult command.

The standard 17-document pipeline (`analyze_project` + `export_markdown`)
does not depend on which variant the user picked at the consult dialog.
This module closes that loop: after standard outputs are generated, the
consultant writes ONE extra document — `REVERSAL_PLAN.md` — produced by
the plugin instantiated with the chosen variant.

Result: picking `cespi_unlp_8state` vs `iso9001_minimalist_5state` produces
materially different reversal plans, both attributable, both auditable.
"""

from __future__ import annotations

from pathlib import Path

from forgemind.plugins import get_plugin_registry
from forgemind.plugins.reverse_state_pattern import ReverseStatePattern
from forgemind.schemas.project import ProjectAnalysis


def instantiate_for_variant(
    plugin_class: type[ReverseStatePattern], variant_id: str | None
) -> ReverseStatePattern:
    """Construct a plugin instance bound to the chosen variant.

    Plugins that accept `variant_id` in their constructor (e.g. the
    ISO 9001 plugin) get the variant honoured. Plugins with a no-arg
    constructor (e.g. the software / ai_ml plugins today) fall back
    silently — their single variant is their default.

    The fallback uses TypeError detection rather than `inspect` so the
    plugin author can keep their constructor signature flexible.
    """
    if variant_id is not None:
        try:
            return plugin_class(variant_id=variant_id)
        except TypeError:
            # Plugin doesn't expose a variant_id kwarg yet — treat its
            # default construction as the (only) variant.
            pass
        except ValueError:
            # variant_id is recognized by the class but unknown to it.
            # Surface this rather than swallow — the caller's history or
            # taxonomy is inconsistent with the plugin and that needs
            # human attention.
            raise
    return plugin_class()


def write_variant_reversal_plan(
    out_dir: Path,
    analysis: ProjectAnalysis,
    variant_id: str | None,
    variant_name: str | None = None,
    variant_source: str | None = None,
    domain_id: str | None = None,
) -> Path | None:
    """Write REVERSAL_PLAN.md to `out_dir` using the chosen variant.

    Args:
        out_dir: Directory where REVERSAL_PLAN.md will be written.
        analysis: The full project analysis (used for state plan inputs).
        variant_id: The taxonomy variant id picked at calibration time.
        variant_name: Human-friendly variant name (for the header).
        variant_source: Variant's upstream source string (for attribution).
        domain_id: The TAXONOMY domain id (e.g. "iso9001"). When omitted,
            falls back to `analysis.metadata.domain` — but those values
            come from the keyword classifier and may not match plugin
            domain ids (the classifier emits "qms_iso" while the plugin
            registers as "iso9001"). The CLI passes the calibrated
            `session.calibration.domain.id` here so the mapping is
            authoritative.

    Returns the written path on success, or None if no plugin exists for
    the resolved domain (in which case a reversal plan would be
    speculation and is intentionally omitted).
    """
    domain = domain_id or analysis.metadata.domain
    registry = get_plugin_registry()
    plugin_class = (
        registry.get_pattern_class(domain)
        if hasattr(registry, "get_pattern_class")
        else None
    )

    # Fall back to the registered singleton's class if the registry doesn't
    # expose the class directly. Keeps the module compatible across
    # plugin registry implementations.
    if plugin_class is None:
        singleton = (
            registry.get_pattern(domain) if registry.has_pattern(domain) else None
        )
        if singleton is None:
            return None
        plugin_class = type(singleton)

    plugin = instantiate_for_variant(plugin_class, variant_id)
    target_path = out_dir / "REVERSAL_PLAN.md"
    target_path.write_text(
        _render(analysis, plugin, variant_id, variant_name, variant_source),
        encoding="utf-8",
    )
    return target_path


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------


def _render(
    analysis: ProjectAnalysis,
    plugin: ReverseStatePattern,
    variant_id: str | None,
    variant_name: str | None,
    variant_source: str | None,
) -> str:
    """Render the reversal plan markdown document."""
    lines: list[str] = [
        f"# {analysis.metadata.name} — Reversal Plan",
        "",
        f"**Domain**: `{analysis.metadata.domain}`  ",
        f"**Plugin**: `{plugin.domain}` (framework: {plugin.framework})  ",
    ]
    if variant_id:
        lines.append(f"**Variant**: `{variant_id}`")
        if variant_name:
            lines[-1] += f" — {variant_name}"
        lines.append("")
        if variant_source:
            lines.append(f"**Variant source**: {variant_source}")
            lines.append("")
    else:
        lines.append("**Variant**: default (no calibrated variant chosen)")
        lines.append("")

    lines.extend(_render_state_machine(plugin))
    lines.extend(_render_current_state_plan(analysis, plugin))
    lines.extend(_render_footer())
    return "\n".join(lines)


def _render_state_machine(plugin: ReverseStatePattern) -> list[str]:
    """Render the variant's state machine as a table."""
    lines = [
        "## State machine",
        "",
        "| State | Reversible | Can revert to | Data loss | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for state in plugin.get_supported_states():
        targets = ", ".join(state.can_revert_to) if state.can_revert_to else "—"
        notes = (state.reason or "").replace("\n", " ").strip()
        lines.append(
            f"| `{state.state_name}` | "
            f"{'yes' if state.reversible else '**no**'} | "
            f"{targets} | "
            f"{state.data_loss or 'none'} | "
            f"{notes} |"
        )
    lines.append("")
    return lines


def _render_current_state_plan(
    analysis: ProjectAnalysis, plugin: ReverseStatePattern
) -> list[str]:
    """If the project declares a current_state, render a concrete plan."""
    current_state = getattr(analysis.input, "current_state", None)
    if not current_state:
        return [
            "## Concrete reversal plan",
            "",
            "_No `current_state` declared in the project. To produce a concrete_",
            "_reversal plan, add `## Current State` to your project markdown and_",
            "_re-run `forgemind consult`._",
            "",
        ]

    try:
        plan = plugin.generate_reversal_plan(project=analysis, current_state=current_state)
    except ValueError as exc:
        return [
            "## Concrete reversal plan",
            "",
            f"_Cannot generate a reversal plan from state `{current_state}`:_",
            f"_{exc}_",
            "",
        ]

    lines = [
        "## Concrete reversal plan",
        "",
        f"- **Rollback path**: `{plan.rollback_path}`",
        f"- **Estimated time**: {plan.total_estimated_time_minutes} minutes",
        f"- **Highest data-loss risk**: {plan.highest_data_loss_risk}",
        f"- **Confidence**: {plan.confidence:.0%}",
    ]
    if plan.approval_gates:
        lines.append(f"- **Approval gates**: {', '.join(plan.approval_gates)}")
    if plan.dependencies:
        lines.append("- **Dependencies**:")
        for dep in plan.dependencies:
            lines.append(f"    - {dep}")
    if plan.constraints:
        lines.append("- **Constraints**:")
        for c in plan.constraints:
            lines.append(f"    - {c}")
    lines.append("")

    if plan.steps:
        lines.append("### Steps")
        lines.append("")
        for step in plan.steps:
            marker = "🔒" if step.approval_required else "✓"
            line = f"{step.step_number}. {marker} {step.action}"
            if step.estimated_time_minutes:
                line += f" *(≈{step.estimated_time_minutes} min)*"
            if step.approval_role:
                line += f" — approver: `{step.approval_role}`"
            lines.append(line)
            if step.notes:
                lines.append(f"    > {step.notes}")
        lines.append("")

    return lines


def _render_footer() -> list[str]:
    return [
        "---",
        "",
        "_This document was generated by `forgemind consult` using the variant_",
        "_you calibrated to. The chosen variant is recorded in_",
        "_`consultant_calibration.json`. Re-run `forgemind consult` if your_",
        "_project context changes._",
        "",
        "_Outputs are STOCHASTIC. For high-stakes decisions, escalate to the_",
        "_contact listed in `CONSULTANT_CALIBRATION.md`._",
    ]
