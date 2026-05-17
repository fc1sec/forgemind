"""Capability Thresholds generator — the 7 hard limits no agent crosses alone.

Implements doctrine D41 (CertOS-SAGA): seven categories of decision the
agentic layer never auto-executes, regardless of operator instruction or
expected efficiency. Anchored in Anthropic RSP v3.0, EU AI Act Art. 14,
NIST AI RMF GOVERN, and UNESCO 2021.
"""

from __future__ import annotations

from forgemind.doctrines import get_doctrine_registry
from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


# T1-T7 — the seven hard thresholds from CertOS-SAGA D41
THRESHOLDS = [
    {
        "id": "T1",
        "name": "Legal signature or institutional representation",
        "examples": [
            "Signing contracts, addenda, or formal letters to clients",
            "Communications to a regulator or competent authority",
            "Any verbal or written representation before authority",
        ],
        "required_signature": "Executive sponsor / legal proxy",
    },
    {
        "id": "T2",
        "name": "Decisions with safety-critical end-user impact",
        "examples": [
            "Release or hold of a regulated product batch",
            "Acceptance or rejection of supplier-delivered product",
            "Closure of a non-conformity classified as end-user-risk",
            "Changes in production, storage or distribution of safety-critical items",
        ],
        "required_signature": "Quality / Process Coordinator + Executive sponsor",
    },
    {
        "id": "T3",
        "name": "Formal closure of CAPA, NC, or audit finding",
        "examples": [
            "Closure of a critical CAPA",
            "Acceptance of a final risk-treatment plan",
            "Closure of an internal or external audit finding",
            "Decision NOT to open a CAPA when a critical supplier failed",
        ],
        "required_signature": "Quality / Process Coordinator",
    },
    {
        "id": "T4",
        "name": "Approval or publication of a controlled QMS document",
        "examples": [
            "Approval of the in-force version of a procedure, policy, role profile, or quality plan",
            "Publication to the official repository (SharePoint / DMS / etc.)",
            "Retirement or obsolescence of an in-force document",
        ],
        "required_signature": "Process owner + Quality Coordinator",
    },
    {
        "id": "T5",
        "name": "Writes to production systems",
        "examples": [
            "Mutating production data in ERP / CRM / ticketing",
            "Issuing regulated invoices or regulatory filings",
            "Changing identity-provider / document-store permissions",
            "Push to `main` of any production repository",
            "Triggering an e-signature workflow with real signers",
        ],
        "required_signature": "System owner + approved change record",
    },
    {
        "id": "T6",
        "name": "Acceptance of high or critical risk",
        "examples": [
            "Accepting (not treating) an AI risk in the AI risk register",
            "Accepting an audit finding without corrective action",
            "Accepting partial non-compliance with an ISO clause",
        ],
        "required_signature": "Executive sponsor with management-review minute",
    },
    {
        "id": "T7",
        "name": "Institutional external communication",
        "examples": [
            "Outbound email to client, authority or critical supplier from an institutional account",
            "Publication on a corporate channel (LinkedIn, website, B2B platform)",
            "Formal response to a complaint or claim",
            "Any output the counterparty could read as official institutional position",
        ],
        "required_signature": "Designated spokesperson per topic",
    },
]


class CapabilityThresholdsGenerator(BaseGenerator):
    """Render the 7 capability-threshold table + agent behaviour protocol."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        return {
            "project": analysis.metadata.name,
            "domain": analysis.metadata.domain,
            "thresholds": THRESHOLDS,
        }

    def _format_markdown_impl(self, data: dict) -> str:
        registry = get_doctrine_registry()
        d41 = registry.get("capability_thresholds")
        d39 = registry.get("agentic_constitution")

        lines = [
            f"# {data['project']} — Capability Thresholds",
            "",
            "> Seven categories of decision this project's agentic layer **NEVER",
            "> auto-executes**, regardless of operator instruction, model",
            "> confidence, or expected efficiency.",
            "",
        ]
        if d41:
            lines.append(
                f"**Doctrine anchor:** {d41.short_id} — {d41.name} "
                f"([source]({d41.source.url}))"
            )
        if d39:
            lines.append(
                f"**Constitutional anchor:** {d39.short_id} — {d39.name} "
                f"([source]({d39.source.url}))"
            )
        lines.extend([
            "",
            "## The 7 hard thresholds",
            "",
        ])

        for t in data["thresholds"]:
            lines.extend([
                f"### {t['id']} · {t['name']}",
                "",
            ])
            for ex in t["examples"]:
                lines.append(f"- {ex}")
            lines.extend([
                "",
                f"**Human signature required:** {t['required_signature']}",
                "",
            ])

        lines.extend([
            "## Agent behaviour when a threshold is detected",
            "",
            "1. **Stop autonomous execution** immediately.",
            "2. **Emit a HITL package** with: requested task, threshold detected,",
            "   the agent's own recommendation (informative only), residual risk.",
            "3. **Deliver to the functional owner** through the documented channel.",
            "4. **Log the event** with timestamp, hash, owner notified.",
            "5. **Do not retry or rephrase** the instruction until human approval is documented.",
            "",
            "The operator who requested the task **cannot override the threshold**",
            "by instructing the agent to \"do it anyway\". Such instructions are",
            "recorded as override attempts and trigger review.",
            "",
            "## Override policy",
            "",
            "The 7 thresholds admit no operational exceptions. Modifications require:",
            "",
            "1. A signed Architecture Decision Record from Executive + Quality.",
            "2. A management-review minute approving the change.",
            "3. A formal version bump (major) of the project's CAPABILITY_THRESHOLDS.md",
            "   with an entry in the project change-log.",
            "",
            "Skills that attempt to bypass thresholds are major non-conformities",
            "in internal audit.",
            "",
            "## Normative anchors",
            "",
        ])
        if d41:
            for anchor in d41.normative_anchors:
                lines.append(f"- {anchor}")

        content = "\n".join(lines)
        return self.add_header(content)


def generate_capability_thresholds(analysis: ProjectAnalysis) -> str:
    """Convenience function for the capability-thresholds markdown."""
    generator = CapabilityThresholdsGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
