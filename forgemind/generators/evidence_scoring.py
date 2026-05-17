"""Evidence Confidence Scoring + Integrity matrix generator.

Implements doctrines D17 (CertOS-SAGA confidence scoring 1-5) and D37
(three-tier integrity: SHA-256 chain, Ed25519 signature, qualified
time-stamp via accredited trust-service provider). Universal — emitted
for every project so acceptance criteria and risk items can reference a
shared evidence scale.

Jurisdiction note: the qualified-timestamp tier (Tier 2) maps to
RFC 3161, eIDAS qualified time-stamps, or national equivalents; the
user picks the regime appropriate to their jurisdiction.
"""

from __future__ import annotations

from forgemind.doctrines import get_doctrine_registry
from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


CONFIDENCE_LEVELS = [
    (1, "Manual reference, source unclear",
     "Indication only — not citable as evidence"),
    (2, "File exists, metadata insufficient",
     "Requires validation before use"),
    (3, "File with date, owner, location",
     "Preliminary evidence — usable with caveats"),
    (4, "System record with identifier and owner",
     "Reliable evidence"),
    (5, "System record with version, hash, vigency, human validation",
     "Strong evidence — auditor-defensible"),
]

PENALTIES = [
    "Expired (past valid_until)",
    "No declared owner",
    "No linkage to a process",
    "No version recorded",
    "Manual capture susceptible to bias",
    "Uncontrolled source (e.g. ad-hoc email attachment)",
]

INTEGRITY_TIERS = [
    {
        "tier": "Tier 0",
        "name": "SHA-256 hash + linked chain",
        "cost": "Near-zero — bundled with the runtime + version control",
        "when": "Day 1 — start of project",
        "covers": "ISO 9001 cl. 7.5 documentation, 9.1 measurement, 10.2 CAPA",
        "stack": "Standard-library hashing + version control",
    },
    {
        "tier": "Tier 1",
        "name": "Ed25519 human signature",
        "cost": "Low — one-time cost of a hardware security key per signer",
        "when": "Day ~21 — once first HITL package needs to be signed",
        "covers": "ISO 9001 cl. 7.5.2, 10.2.1; ISO 13485 cl. 4.1",
        "stack": "Crypto library + hardware key (e.g. FIDO2 / smartcard / HSM)",
    },
    {
        "tier": "Tier 2",
        "name": "Qualified time-stamp via accredited trust-service provider",
        "cost": "Annual subscription to a qualified trust-service provider",
        "when": "Day 60+ — apply selectively to critical artefacts",
        "covers": "RFC 3161 baseline; eIDAS qualified time-stamps, FDA 21 CFR Part 11, or national equivalents per jurisdiction",
        "stack": "Trust-service-provider integration (pick from accredited list in your jurisdiction)",
    },
    {
        "tier": "Tier 3",
        "name": "Blockchain anchoring (NOT recommended in MVP)",
        "cost": "High operational + governance overhead",
        "when": "Only if an external client / auditor mandates it explicitly",
        "covers": "Adds no incremental value over Tier 2 for most use cases",
        "stack": "External chain provider",
    },
]


class EvidenceScoringGenerator(BaseGenerator):
    """Render the evidence confidence + integrity matrix."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        return {
            "project": analysis.metadata.name,
            "domain": analysis.metadata.domain,
            "confidence_levels": CONFIDENCE_LEVELS,
            "penalties": PENALTIES,
            "integrity_tiers": INTEGRITY_TIERS,
        }

    def _format_markdown_impl(self, data: dict) -> str:
        registry = get_doctrine_registry()
        d17 = registry.get("evidence_confidence_scoring")
        d37 = registry.get("evidence_integrity_hash")

        lines = [
            f"# {data['project']} — Evidence Scoring & Integrity",
            "",
            "> Confidence scale + integrity tiers any artefact in this project",
            "> can be tagged against. Use these scores in `ACCEPTANCE_CRITERIA.md`",
            "> and `RISK_REGISTER.md` to make evidence quality itself auditable.",
            "",
        ]
        if d17:
            lines.append(
                f"**Confidence-scoring anchor:** {d17.short_id} — {d17.name} "
                f"([source]({d17.source.url}))"
            )
        if d37:
            lines.append(
                f"**Integrity anchor:** {d37.short_id} — {d37.name} "
                f"([source]({d37.source.url}))"
            )
        lines.extend([
            "",
            "## Confidence scale (1-5)",
            "",
            "| Level | Criterion | Use |",
            "|---|---|---|",
        ])
        for level, criterion, use in data["confidence_levels"]:
            lines.append(f"| {level} | {criterion} | {use} |")

        lines.extend([
            "",
            "## Penalties (downgrade the score)",
            "",
        ])
        for p in data["penalties"]:
            lines.append(f"- {p}")

        lines.extend([
            "",
            "## Live-evidence minimal fields",
            "",
            "Any evidence item handled in this project should carry at minimum:",
            "",
            "```yaml",
            "evidence_id:",
            "title:",
            "source_system:",
            "source_location:",
            "created_at:",
            "captured_at:",
            "author_or_owner:",
            "process:",
            "iso_clause:",
            "document_code:",
            "version:",
            "status:           # detected | pending_validation | validated | in_force | expired | obsolete | rejected | requires_update",
            "valid_until:",
            "responsible:",
            "confidence_level: # 1..5",
            "human_validated:  # true | false",
            "hash_or_identifier:",
            "```",
            "",
            "## Integrity tiers (three austere levels)",
            "",
            "| Tier | Name | Cost | When | Stack |",
            "|---|---|---|---|---|",
        ])
        for t in data["integrity_tiers"]:
            lines.append(
                f"| {t['tier']} | {t['name']} | {t['cost']} | {t['when']} | {t['stack']} |"
            )

        lines.extend([
            "",
            "## Choosing a tier",
            "",
            "- Tier 0 is **mandatory** from day 1 for every artefact this project produces.",
            "- Tier 1 is **required** before the first HITL-signed package leaves the team.",
            "- Tier 2 is **selective** — apply only to legally / regulatorily critical artefacts.",
            "- Tier 3 is **discouraged** unless externally mandated.",
            "",
            "## Integrity-bearing evidence fields (additions to the minimal schema)",
            "",
            "```yaml",
            "hash_sha256:",
            "hash_prev_event:        # link in the chain (Tier 0)",
            "signed_by:              # role or human id (Tier 1)",
            "signed_at:",
            "signature_alg:          # ed25519",
            "psc_constancia_id:      # Tier 2",
            "psc_provider:           # Tier 2",
            "```",
            "",
            "## Normative anchors",
            "",
        ])
        if d17:
            for a in d17.normative_anchors:
                lines.append(f"- {a}")
        if d37:
            for a in d37.normative_anchors:
                lines.append(f"- {a}")

        content = "\n".join(lines)
        return self.add_header(content)


def generate_evidence_scoring(analysis: ProjectAnalysis) -> str:
    """Convenience function for the evidence-scoring markdown."""
    generator = EvidenceScoringGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
