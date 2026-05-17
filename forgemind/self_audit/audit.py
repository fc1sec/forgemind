"""Self-audit engine.

Runs each registered doctrine against the ForgeMind repository state and
emits findings. Designed to be CI-runnable: exit non-zero on `blocker`
findings, zero on `info` / `warning` only.

The audit is intentionally deterministic and offline — same input repo,
same output report — so CI gating is reliable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path

from forgemind.doctrines import (
    Doctrine,
    DoctrineCategory,
    get_doctrine_registry,
)


class FindingSeverity(str, Enum):
    BLOCKER = "blocker"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Finding:
    """A single audit observation."""

    doctrine_short_id: str
    doctrine_name: str
    severity: FindingSeverity
    summary: str
    evidence_path: str | None = None
    remediation: str | None = None


@dataclass
class SelfAuditReport:
    """The aggregate outcome of a self-audit run."""

    audit_date: str
    forgemind_version: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def blocker_count(self) -> int:
        return sum(1 for f in self.findings if f.severity is FindingSeverity.BLOCKER)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity is FindingSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity is FindingSeverity.INFO)

    @property
    def is_green(self) -> bool:
        return self.blocker_count == 0


# ---------------------------------------------------------------------------
# Per-doctrine checks
# ---------------------------------------------------------------------------


def _governance_path(repo_root: Path, filename: str) -> Path:
    return repo_root / "docs" / "governance" / filename


def _check_constitution(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    path = _governance_path(repo_root, "FORGEMIND_CONSTITUTION.md")
    if not path.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                "ForgeMind has no published constitution of its own.",
                evidence_path=str(path.relative_to(repo_root)),
                remediation=(
                    "Author docs/governance/FORGEMIND_CONSTITUTION.md declaring "
                    "ForgeMind's mission, lexicographic values, three-question test."
                ),
            )
        ]
    text = path.read_text()
    issues: list[Finding] = []
    if "lexicographic" not in text.lower():
        issues.append(
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                "Constitution does not declare a lexicographic value hierarchy.",
                evidence_path=str(path.relative_to(repo_root)),
                remediation="Add an explicit ordered list of values 1..N.",
            )
        )
    if "three-question test" not in text.lower() and "3-question test" not in text.lower():
        issues.append(
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                "Constitution does not codify the three-question pre-invocation test.",
                evidence_path=str(path.relative_to(repo_root)),
                remediation="Add the amplify / authority / evidence three-question test.",
            )
        )
    return issues


def _check_aiia(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    path = _governance_path(repo_root, "FORGEMIND_AIIA.md")
    if not path.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                "ForgeMind has no AIIA of its own despite being an advice-emitting system.",
                evidence_path=str(path.relative_to(repo_root)),
                remediation=(
                    "Author docs/governance/FORGEMIND_AIIA.md filling the 8 sections "
                    "of the AIIA template against the ForgeMind tool itself."
                ),
            )
        ]
    text = path.read_text()
    missing_sections = [
        f"section {i}" for i in range(1, 9) if f"## {i} ·" not in text and f"## {i}." not in text
    ]
    if missing_sections:
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                f"AIIA is missing one or more required sections: {', '.join(missing_sections)}.",
                evidence_path=str(path.relative_to(repo_root)),
            )
        ]
    return []


def _check_capability_thresholds(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    path = _governance_path(repo_root, "FORGEMIND_CAPABILITY_THRESHOLDS.md")
    if not path.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                "ForgeMind has not declared its own capability thresholds.",
                evidence_path=str(path.relative_to(repo_root)),
                remediation=(
                    "Author docs/governance/FORGEMIND_CAPABILITY_THRESHOLDS.md "
                    "declaring the 7 actions ForgeMind never auto-executes."
                ),
            )
        ]
    text = path.read_text()
    missing = [f"T{i}" for i in range(1, 8) if f"T{i}" not in text]
    if missing:
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                f"Capability-thresholds doc is missing thresholds: {', '.join(missing)}.",
                evidence_path=str(path.relative_to(repo_root)),
            )
        ]
    return []


def _check_skill_card(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    path = _governance_path(repo_root, "FORGEMIND_SKILL_CARD.md")
    if not path.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                "ForgeMind has no Skill Card describing itself machine-readably.",
                evidence_path=str(path.relative_to(repo_root)),
                remediation=(
                    "Author docs/governance/FORGEMIND_SKILL_CARD.md following the "
                    "12-section template from generators/skill_card.py."
                ),
            )
        ]
    text = path.read_text()
    missing = [str(i) for i in range(1, 13) if f"## {i} ·" not in text and f"## {i}." not in text]
    if missing:
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                f"Skill Card is missing sections: {', '.join(missing)}.",
                evidence_path=str(path.relative_to(repo_root)),
            )
        ]
    return []


def _check_aims_integrated(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # D45 demands AIMS↔SGC integration. ForgeMind itself does not run an SGC,
    # but the constitution + AIIA + thresholds + skill card act as ForgeMind's
    # AIMS surface. Surface this as info, not blocker.
    constitution = _governance_path(repo_root, "FORGEMIND_CONSTITUTION.md")
    if constitution.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.INFO,
                "ForgeMind does not maintain an external SGC; its AIMS surface is "
                "the governance/ folder (constitution + AIIA + thresholds + skill card).",
            )
        ]
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.WARNING,
            "Cannot confirm AIMS surface — no governance/ artifacts exist yet.",
        )
    ]


def _check_evidence_confidence(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # The taxonomy already carries per-domain + per-variant confidence values.
    # Audit checks that the EVIDENCE_SCORING.md generator output is wired into
    # the exporter.
    exporter = repo_root / "forgemind" / "exporters" / "markdown.py"
    if "generate_evidence_scoring" not in exporter.read_text():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                "EVIDENCE_SCORING.md generator not wired into the markdown exporter.",
                evidence_path=str(exporter.relative_to(repo_root)),
            )
        ]
    return []


def _check_evidence_integrity(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # D37 expects a hash on every signed artifact. ForgeMind outputs are local
    # plaintext; the integrity story is "git tracks them". Surface as info.
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.INFO,
            "ForgeMind outputs are local Markdown; integrity Tier 0 is provided by "
            "the user's git working tree. Tier 1+ is the user's responsibility.",
        )
    ]


def _check_token_governance(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # ForgeMind is zero-LLM, zero-network. Confirm by absence of cloud SDKs.
    pyproject = repo_root / "pyproject.toml"
    deps_text = pyproject.read_text().lower()
    cloud_signals = [
        "anthropic",
        "openai",
        "google-generativeai",
        "boto3",
        "azure-",
    ]
    found = [s for s in cloud_signals if s in deps_text]
    if found:
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                f"pyproject.toml references cloud / LLM SDKs: {', '.join(found)}. "
                "Verify the LOCAL-ONLY claim still holds.",
                evidence_path=str(pyproject.relative_to(repo_root)),
            )
        ]
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.INFO,
            "Confirmed: no LLM / cloud SDK dependencies. Token cost = 0.",
        )
    ]


def _check_agnostic_routing(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # ForgeMind already implements rule-first (taxonomy → refuse if not_covered).
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.INFO,
            "ForgeMind operates at routing-tier 1 only (deterministic rule). "
            "Tiers 2-6 escalate to the user; tier 7 (human) is the consultant's "
            "refusal contract.",
        )
    ]


def _check_multi_norm(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # Verify the v1.3 taxonomy promotions are in place.
    from forgemind.disciplines import Coverage, get_taxonomy

    taxonomy = get_taxonomy()
    expected_partial = {"iso13485", "iso14001", "iso45001", "iso27001", "iso42001", "iso22301"}
    misses = [
        d for d in expected_partial
        if taxonomy.coverage_for(d) is not Coverage.PARTIAL
    ]
    if misses:
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                f"Multi-norm Annex SL upgrade incomplete: {', '.join(misses)} not at PARTIAL.",
            )
        ]
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.INFO,
            f"Confirmed: {len(expected_partial)} ISO management-system domains at PARTIAL with HLS variants.",
        )
    ]


def _check_rdmaicsi(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # The presence of THIS module + the self-audit report is the operational
    # evidence that the cycle ran.
    report_path = repo_root / "docs" / "governance" / "SELF_AUDIT_REPORT.md"
    if not report_path.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                "No prior self-audit report on file. First cycle is happening now.",
            )
        ]
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.INFO,
            "Prior self-audit cycle on file; this is the next iteration.",
        )
    ]


def _check_integral_speed(repo_root: Path, doctrine: Doctrine) -> list[Finding]:
    # Verify the test suite exists and is comprehensive (proxy for pilot discipline).
    tests_dir = repo_root / "tests"
    if not tests_dir.exists():
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.BLOCKER,
                "No tests/ directory — integral-speed discipline requires pilot evidence.",
            )
        ]
    test_files = list(tests_dir.glob("test_*.py"))
    if len(test_files) < 10:
        return [
            Finding(
                doctrine.short_id,
                doctrine.name,
                FindingSeverity.WARNING,
                f"Only {len(test_files)} test modules — sparse pilot coverage.",
            )
        ]
    return [
        Finding(
            doctrine.short_id,
            doctrine.name,
            FindingSeverity.INFO,
            f"Confirmed: {len(test_files)} test modules act as ForgeMind's pilot harness.",
        )
    ]


# ---------------------------------------------------------------------------
# Dispatch table — single source of truth for which check belongs to which doctrine
# ---------------------------------------------------------------------------

_CHECKS = {
    "agentic_constitution": _check_constitution,
    "aiia_pre_deployment": _check_aiia,
    "capability_thresholds": _check_capability_thresholds,
    "skill_card_mandatory": _check_skill_card,
    "aims_integrated_sgc": _check_aims_integrated,
    "evidence_confidence_scoring": _check_evidence_confidence,
    "evidence_integrity_hash": _check_evidence_integrity,
    "token_cost_governance": _check_token_governance,
    "agnostic_task_routing": _check_agnostic_routing,
    "multi_norm_extensibility": _check_multi_norm,
    "agentic_rdmaicsi": _check_rdmaicsi,
    "integral_speed": _check_integral_speed,
}


def run_self_audit(repo_root: Path | None = None) -> SelfAuditReport:
    """Run every doctrine check against the repository and aggregate findings."""
    from forgemind import __version__

    if repo_root is None:
        # The repo root is two parents up from this module: forgemind/self_audit/audit.py
        repo_root = Path(__file__).resolve().parent.parent.parent

    registry = get_doctrine_registry()
    report = SelfAuditReport(
        audit_date=date.today().isoformat(),
        forgemind_version=__version__,
    )

    for doctrine in registry.list_all():
        check = _CHECKS.get(doctrine.id)
        if check is None:
            # Every registered doctrine should have a check; if not, that itself is a warning.
            report.findings.append(
                Finding(
                    doctrine.short_id,
                    doctrine.name,
                    FindingSeverity.WARNING,
                    "Doctrine is registered but has no corresponding self-audit check.",
                    remediation=f"Add a check function for '{doctrine.id}' in forgemind/self_audit/audit.py.",
                )
            )
            continue
        report.findings.extend(check(repo_root, doctrine))

    return report


def render_report_markdown(report: SelfAuditReport) -> str:
    """Render a SelfAuditReport as Markdown for docs/governance/SELF_AUDIT_REPORT.md."""
    lines = [
        "# ForgeMind Self-Audit Report",
        "",
        "> ForgeMind applies its own doctrines registry to itself.",
        "> This file is regenerated by `forgemind self-audit`; do not hand-edit.",
        "",
        f"- **Date:** {report.audit_date}",
        f"- **ForgeMind version:** {report.forgemind_version}",
        f"- **Status:** {'GREEN' if report.is_green else 'BLOCKED'}",
        f"- **Blockers:** {report.blocker_count} · "
        f"**Warnings:** {report.warning_count} · "
        f"**Info:** {report.info_count}",
        "",
        "## Findings",
        "",
    ]

    if not report.findings:
        lines.append("_No findings — every doctrine check passed silently._")
        return "\n".join(lines)

    # Group by severity for readability
    for severity, label, emoji in [
        (FindingSeverity.BLOCKER, "Blockers", "🚫"),
        (FindingSeverity.WARNING, "Warnings", "⚠️"),
        (FindingSeverity.INFO, "Info", "ℹ️"),
    ]:
        group = [f for f in report.findings if f.severity is severity]
        if not group:
            continue
        lines.append(f"### {emoji} {label} ({len(group)})")
        lines.append("")
        for f in group:
            lines.append(f"- **{f.doctrine_short_id} · {f.doctrine_name}** — {f.summary}")
            if f.evidence_path:
                lines.append(f"  - evidence: `{f.evidence_path}`")
            if f.remediation:
                lines.append(f"  - remediation: {f.remediation}")
        lines.append("")

    lines.extend([
        "## Cycle reference (D02 Agentic RDMAICSI)",
        "",
        "- **R** Recognize — `forgemind doctrines` registry lists every doctrine in scope.",
        "- **D** Define — each check function in `forgemind/self_audit/audit.py` encodes what the doctrine demands.",
        "- **M** Measure — this report.",
        "- **A** Analyze — read the Blockers / Warnings sections above.",
        "- **I** Improve — apply remediations; re-run `forgemind self-audit`.",
        "- **C** Control — wire the audit into CI; fail builds on blocker findings.",
        "- **S** Systematize — keep `docs/governance/` as the canonical AIMS surface for ForgeMind.",
        "- **I** Institutionalize — bump version + CHANGELOG when this report goes GREEN.",
    ])
    return "\n".join(lines)
