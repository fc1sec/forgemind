"""Skill Card generator — machine-readable manual per sub-agent.

Implements doctrine D43 (CertOS-SAGA): a 12-section, machine-readable
"instructions for use" template that must be published before any custom
AI skill is callable by anyone other than its implementer. Aligns with
EU AI Act Art. 13 (instructions for use), OECD AI Principles (transparency),
ISO/IEC 42001:2023 §7.5 (documented information), and ISO 9001:2015 cl. 7.5.
"""

from __future__ import annotations

from forgemind.doctrines import get_doctrine_registry
from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


class SkillCardGenerator(BaseGenerator):
    """Render the 12-section Skill Card template."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        return {
            "project": analysis.metadata.name,
            "slug": analysis.metadata.slug,
            "domain": analysis.metadata.domain,
            "objective": analysis.input.objective,
        }

    def _format_markdown_impl(self, data: dict) -> str:
        registry = get_doctrine_registry()
        d43 = registry.get("skill_card_mandatory")
        d39 = registry.get("agentic_constitution")

        lines = [
            f"# Skill Card — {data['project']}",
            "",
            "> Machine-readable manual for this AI skill / agent. Publish BEFORE",
            "> the skill is callable by anyone other than its implementer.",
            "",
        ]
        if d43:
            lines.append(
                f"**Doctrine anchor:** {d43.short_id} — {d43.name} "
                f"([source]({d43.source.url}))"
            )
        lines.extend([
            "",
            "## 1 · Identification",
            "",
            f"- **Slug:** `{data['slug']}`",
            f"- **Full name:** {data['project']}",
            "- **Skill version (semver):** v0.1.0 (pilot)",
            "- **AIIA reference + hash:** AIIA-NNN-_____ · sha256: _____",
            "- **Release date:** _____",
            "- **Status:** ☐ PILOT  ☐ PRODUCTION  ☐ DEPRECATED  ☐ SUSPENDED",
            "",
            "## 2 · Declared Purpose (constitutional)",
            "",
            f"- **Operational problem solved:** {data['objective']}",
            "- **How it AMPLIFIES human capacity (D39 reverse-citation):** _____",
            "- **Which project / organisational principle it materialises:** _____",
            "",
            "## 3 · Owners",
            "",
            "- **Functional owner (role):** _____",
            "- **Technical owner (implementer):** _____",
            "- **Escalation contact** (channel + identifier): _____",
            "",
            "## 4 · Underlying model",
            "",
            "- **Model name and version:** Claude Opus 4.7 / Sonnet 4.6 / Haiku 4.5 / ____",
            "- **Choice rationale** (capability vs. cost vs. latency): _____",
            "- **Provider safety level at release:** ASL-2 / ASL-3 / ____",
            "- **Configuration** (temperature, system-prompt summary, active MCPs): _____",
            "",
            "## 5 · Declared capabilities",
            "",
            "Exhaustive list of tasks the skill executes. Per task: expected",
            "input type, delivered output type.",
            "",
            "1. _Task_ → input: _____ → output: _____",
            "2. _Task_ → input: _____ → output: _____",
            "",
            "## 6 · Explicit limits",
            "",
            "- Tasks the skill **does NOT** execute (include applicable capability",
            "  thresholds T1-T7 from CAPABILITY_THRESHOLDS.md): _____",
            "- Input types rejected: _____",
            "- Minimum confidence below which the skill escalates HITL: _____",
            "",
            "## 7 · Data accessed",
            "",
            "- **Document / file sources** (which folders, mailboxes): _____",
            "- **System sources** (modules / endpoints / scope read/write): _____",
            "- **External sources** (web, APIs, MCPs): _____",
            "- **PII categories potentially accessed** (category, NOT content): _____",
            "- **Retention perimeter** (what is logged, where, for how long): _____",
            "",
            "## 8 · Accuracy metrics",
            "",
            "- Expected baseline average confidence: _____",
            "- Known hallucination rates (if measured): _____",
            "- Red-team coverage (last date, result, open defects): _____",
            "- Observed human-rework rate: _____",
            "",
            "## 9 · Safe-use assumptions",
            "",
            "- Expected input state (clean / validated / in format X): _____",
            "- Operating conditions (connectivity required? authenticated user? business hours?): _____",
            "- Out-of-scope cases where the skill **silently degrades** and why",
            "  its output must not be assumed valid: _____",
            "",
            "## 10 · Fallback plan",
            "",
            "- What to do if the skill fails (manual backup process): _____",
            "- What to do if the skill is suspended (containment state): _____",
            "- Who approves re-activation: _____",
            "",
            "## 11 · Version history",
            "",
            "| Version | Date | Material changes | AIIA updated? | Approver |",
            "|---|---|---|---|---|",
            "| v0.1.0 | _____ | Initial pilot | _____ | _____ |",
            "",
            "## 12 · Integrity hash & signature",
            "",
            "- **SHA-256** of this CARD at approval time: _____",
            "- **Ed25519 signature** of functional owner: _____",
            "- **Signature block (auditor-readable):**",
            "  ```",
            "  -----BEGIN SKILL CARD SIGNATURE-----",
            "  signer: _____",
            "  algorithm: ed25519",
            "  timestamp: _____",
            "  hash_sha256: _____",
            "  signature: _____",
            "  -----END SKILL CARD SIGNATURE-----",
            "  ```",
            "",
            "## Runtime presentation",
            "",
            "An ≤100-word executive summary of sections 1, 2, 5, 6, 9 must be",
            "shown to the operator the FIRST TIME they invoke this skill in a",
            "session, and must be re-consultable on demand. Without a published",
            "CARD, invocation must be refused.",
            "",
            "## Normative anchors",
            "",
        ])
        if d43:
            for anchor in d43.normative_anchors:
                lines.append(f"- {anchor}")

        content = "\n".join(lines)
        return self.add_header(content)


def generate_skill_card(analysis: ProjectAnalysis) -> str:
    """Convenience function for the skill-card markdown."""
    generator = SkillCardGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
