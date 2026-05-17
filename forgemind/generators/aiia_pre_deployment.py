"""AIIA (AI Impact Assessment) pre-deployment generator.

Implements doctrine D40 (CertOS-SAGA): an eight-section pre-deployment gate
anchored in ISO/IEC 42001:2023 §6.1.4, NIST AI RMF GenAI Profile (AI 600-1)
MAP function, and EU AI Act Art. 9 (Risk management for high-risk AI).

The output is a TEMPLATE the user fills in before promoting an AI system
from sandbox to shared use. ForgeMind never fabricates the answers — it
emits the structure plus targeted prompts derived from the project analysis.
"""

from __future__ import annotations

from forgemind.doctrines import get_doctrine_registry
from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


# 12 GenAI risks from NIST AI 600-1 (July 2024 GenAI Profile)
NIST_GENAI_RISKS = [
    "Confabulation (hallucination)",
    "Data Privacy",
    "Harmful Bias",
    "Information Integrity",
    "Information Security",
    "Intellectual Property",
    "Value Chain Integration",
    "Environmental Impact",
    "Human-AI Configuration",
    "Dangerous, Violent or Hateful content",
    "Obscene or Degrading content",
    "CBRN / weapon-material information",
]


_AI_DOMAINS = {"ai_project", "ai_ml", "llm_agents", "classical_ml"}


class AIIAGenerator(BaseGenerator):
    """Generate an AIIA pre-deployment template for AI/ML projects."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        domain = analysis.metadata.domain
        is_ai_domain = domain in _AI_DOMAINS

        return {
            "project": analysis.metadata.name,
            "domain": domain,
            "is_ai_domain": is_ai_domain,
            "objective": analysis.input.objective,
            "stakeholders_raw": analysis.input.stakeholders or "Not specified",
            "constraints_raw": analysis.input.constraints,
            "top_risks": [r.get("risk", "") for r in analysis.risks[:5]],
            "nist_genai_risks": NIST_GENAI_RISKS,
        }

    def _format_markdown_impl(self, data: dict) -> str:
        registry = get_doctrine_registry()
        d40 = registry.get("aiia_pre_deployment")
        d39 = registry.get("agentic_constitution")

        applies_note = (
            "This project's domain is AI/ML — an AIIA is **mandatory** before any"
            " shared use of the system.\n"
            if data["is_ai_domain"]
            else "This project's domain is not classified as AI/ML. The AIIA below"
            " is provided as a **defensive option** for any AI-supported feature"
            " inside the work. Skip it if no AI system is being deployed.\n"
        )

        lines = [
            f"# {data['project']} — AI Impact Assessment (AIIA)",
            "",
            "> Pre-deployment gate. Complete BEFORE promoting any AI agent / skill /",
            "> MCP server / agentic automation from sandbox to shared use.",
            "",
            f"**Doctrine anchor:** {d40.short_id} — {d40.name} "
            f"([source]({d40.source.url}))" if d40 else "",
            f"**Constitutional anchor:** {d39.short_id} — {d39.name} "
            f"([source]({d39.source.url}))" if d39 else "",
            "",
            applies_note,
            "## 1 · AI System Identification",
            "",
            "- **System name:** _____",
            "- **Version / model:** Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5 / ____",
            "- **Functional owner (role):** _____",
            "- **Technical owner (implementer):** _____",
            "- **Proposed deployment date:** _____",
            "",
            "## 2 · Declared Purpose",
            "",
            f"- **Operational problem solved:** {data['objective']}",
            "- **How does this AMPLIFY human capacity** (D39 reverse-citation)? _____",
            "- **Which SAGA principle does it materialise** (cite project vision)? _____",
            "",
            "## 3 · Affected Stakeholders",
            "",
            "| Stakeholder | Expected impact | Residual risk |",
            "|---|---|---|",
            "| End user / patient | direct / indirect / none | _____ |",
            "| Customer / client | _____ | _____ |",
            "| Internal team (which roles) | _____ | _____ |",
            "| Critical supplier | _____ | _____ |",
            "| Other | _____ | _____ |",
            "",
            f"Recorded stakeholders from project: {data['stakeholders_raw']}",
            "",
            "## 4 · Risk Map (NIST AI 600-1 GenAI Profile)",
            "",
            "For each risk that applies, record probability (1-5), impact (1-5),",
            "compensating control, and control owner.",
            "",
            "| GenAI Risk | Applies? | Probability | Impact | Control | Owner |",
            "|---|---|---|---|---|---|",
        ]

        for risk in data["nist_genai_risks"]:
            lines.append(f"| {risk} | ☐ | _ | _ | _____ | _____ |")

        lines.extend([
            "",
            "### Project-level top risks already detected",
        ])
        if data["top_risks"]:
            for r in data["top_risks"]:
                lines.append(f"- {r}")
        else:
            lines.append("- _(no risks recorded in project analysis yet)_")

        lines.extend([
            "",
            "## 5 · EU AI Act Categorisation (voluntary reference)",
            "",
            "- ☐ High-risk system per Annex III? _(yes / no — justify)_",
            "- ☐ General-purpose AI (GPAI)? cite underlying model",
            "- If high-risk: declare alignment with Arts. 9, 13, 14, 15",
            "",
            "## 6 · Binding Controls",
            "",
            "- HITL gates per project Human-Review Matrix",
            "- Capability thresholds that apply: T1 / T2 / T3 / T4 / T5 / T6 / T7 (see CAPABILITY_THRESHOLDS.md)",
            "- **Reversal plan documented** — how the system is disabled, cost to disable, who approves re-activation",
            "- **Minimum logging:** input hash, output hash, timestamp, owner notified",
            "- **Skill Card published** before deployment (see SKILL_CARD.md)",
            "- **First red-team exercise scheduled** within 30 days of deployment",
            "",
            "## 7 · Pilot Plan",
            "",
            "- **Pilot population:** authorised users, duration, success/abandon metrics",
            "- **Promotion-to-production criteria:** _____",
            "- **Abort criteria (kill switch):** _____",
            "- **Management review minute** approving the pilot: _____",
            "",
            "## 8 · Approvals",
            "",
            "| Role | Signature | Date | Hash of signed artefact |",
            "|---|---|---|---|",
            "| Quality / Process Coordinator | _____ | _____ | _____ |",
            "| Executive / DG sponsor | _____ | _____ | _____ |",
            "| Functional owner | _____ | _____ | _____ |",
            "| Technical lead | _____ | _____ | _____ |",
            "",
            "## Normative anchors",
            "",
        ])
        if d40:
            for anchor in d40.normative_anchors:
                lines.append(f"- {anchor}")

        lines.extend([
            "",
            "## Hard limit",
            "",
            "**No custom AI skill / agent may be invoked by anyone other than its",
            "implementer until this AIIA is approved and archived with an",
            "integrity hash.** Skills without an approved AIIA generate a major",
            "non-conformity in internal audit.",
            "",
        ])

        content = "\n".join(line for line in lines if line is not None)
        return self.add_header(content)


def generate_aiia_pre_deployment(analysis: ProjectAnalysis) -> str:
    """Convenience function to generate the AIIA pre-deployment markdown."""
    generator = AIIAGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
