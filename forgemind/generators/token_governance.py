"""Token & Cost Governance routing card.

Implements doctrines D22 (token governance — 5-level routing) and D06
(agnostic task routing — 7-step decision hierarchy). Universal —
emitted for every project so design decisions can defer LLM calls
behind a deterministic ladder.
"""

from __future__ import annotations

from forgemind.doctrines import get_doctrine_registry
from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis

DECISION_LEVELS = [
    (0, "Pure rule",
     "Document expired by date · field-presence check · count threshold",
     "No"),
    (1, "Join / metadata",
     "Supplier in ERP missing dossier in DMS · part without QA record",
     "No"),
    (2, "Short text extraction",
     "Extract code + version from a filename · pull a date from a header",
     "Optional (parser preferred)"),
    (3, "Contextual judgment",
     "Is the evidence sufficient for ISO clause X? · classify a complaint type",
     "Yes (with cached document summary)"),
    (4, "Critical dictum",
     "CAPA root-cause draft · high-risk decision narrative · audit finding",
     "Yes (with mandatory human validation)"),
]


ROUTING_HIERARCHY = [
    "Deterministic rule if it suffices",
    "Structured query if the source allows",
    "Local parser / extractor if the format is known",
    "Cache / index if already analysed",
    "Small / cheap model if classification or extraction is repeatable",
    "Strong model if ambiguity, reasoning, critical synthesis or audit",
    "Human if authority, risk, approval or operational change is implied",
]


SAVINGS_RULES = [
    "Cache by hash — never re-summarise an unchanged document",
    "Persistent summary per document — reuse across runs",
    "Excerpts before full document — bound the context window",
    "Short prompt with explicit output contract (structured schema)",
    "Structured response (JSON / YAML) preferred over free text",
    "Don't use an LLM if a rule suffices",
    "Sampling at high volume — validate the rest by audit, not exhaustive call",
]


QUALITY_GUARDS = [
    "Has a clear output schema",
    "Has an automated test",
    "Has evidence of sufficient precision (sampled or measured)",
    "Has a fallback to a stronger model or human",
    "Does NOT drive a critical decision unsupervised",
]


class TokenGovernanceGenerator(BaseGenerator):
    """Render the cost-governance + agnostic-routing card."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        return {
            "project": analysis.metadata.name,
            "domain": analysis.metadata.domain,
            "decision_levels": DECISION_LEVELS,
            "routing_hierarchy": ROUTING_HIERARCHY,
            "savings_rules": SAVINGS_RULES,
            "quality_guards": QUALITY_GUARDS,
        }

    def _format_markdown_impl(self, data: dict) -> str:
        registry = get_doctrine_registry()
        d22 = registry.get("token_cost_governance")
        d06 = registry.get("agnostic_task_routing")

        lines = [
            f"# {data['project']} — Token & Cost Governance",
            "",
            "> Treat LLM tokens as a quality resource, not a technical cost.",
            "> Route each decision to the cheapest tier that preserves quality.",
            "",
        ]
        if d22:
            lines.append(
                f"**Cost-governance anchor:** {d22.short_id} — {d22.name} "
                f"([source]({d22.source.url}))"
            )
        if d06:
            lines.append(
                f"**Routing anchor:** {d06.short_id} — {d06.name} "
                f"([source]({d06.source.url}))"
            )
        lines.extend([
            "",
            "## Decision levels (which tier handles which decision)",
            "",
            "| Level | Description | Example | LLM? |",
            "|---|---|---|---|",
        ])
        for lvl, desc, example, llm in data["decision_levels"]:
            lines.append(f"| {lvl} | {desc} | {example} | {llm} |")

        lines.extend([
            "",
            "## 7-step routing hierarchy (try in order)",
            "",
        ])
        for i, step in enumerate(data["routing_hierarchy"], 1):
            lines.append(f"{i}. {step}")

        lines.extend([
            "",
            "## Cost-savings rules",
            "",
        ])
        for r in data["savings_rules"]:
            lines.append(f"- {r}")

        lines.extend([
            "",
            "## Quality guard before downgrading a task to a cheaper tier",
            "",
            "A task may be moved to a cheaper tier ONLY if **all** of the following hold:",
            "",
        ])
        for g in data["quality_guards"]:
            lines.append(f"- ☐ {g}")

        lines.extend([
            "",
            "## Per-task routing contract (log per call)",
            "",
            "Every LLM-eligible call this project makes should record:",
            "",
            "```yaml",
            "task:",
            "source:",
            "method_chosen:",
            "methods_discarded:",
            "estimated_cost:",
            "risk:",
            "confidence:",
            "validation_required:   # rule | test | sampling | human",
            "test_applied:",
            "output_summary:",
            "```",
            "",
            "## Suggested budgets to declare",
            "",
            "- per run",
            "- per day",
            "- per source / process",
            "- per agent",
            "- per critical ISO clause (or domain artefact)",
            "",
            "## Suggested indicators",
            "",
            "- % gaps resolved without an LLM call",
            "- LLM calls per run",
            "- Estimated cost per audit / decision package",
            "- Re-analyses avoided by cache hits",
            "- Evidence items with an in-force summary",
            "- Human decisions prepared per token spent",
            "",
            "## Fallback when a tool / method fails",
            "",
            "1. Retry with the cache or an alternative source",
            "2. Reduce the scope of the request",
            "3. Escalate to a stronger model if the value justifies the cost",
            "4. Request human review if there is critical impact",
            "5. Record the limitation in the project log",
            "",
            "## Normative anchors",
            "",
        ])
        if d22:
            for a in d22.normative_anchors:
                lines.append(f"- {a}")
        if d06:
            for a in d06.normative_anchors:
                lines.append(f"- {a}")

        content = "\n".join(lines)
        return self.add_header(content)


def generate_token_governance(analysis: ProjectAnalysis) -> str:
    """Convenience function for the token-governance markdown."""
    generator = TokenGovernanceGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
