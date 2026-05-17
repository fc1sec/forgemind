"""Self-audit module — ForgeMind applies its own doctrines to itself.

The self-audit is the operationalisation of D02 (Agentic RDMAICSI) inside
ForgeMind: each release cycle, the project re-checks that every doctrine
in `forgemind/data/doctrines.yaml` is honoured by the codebase that ships.

This is not a vanity check — it's the only way the doctrines registry
remains a load-bearing reference rather than decorative documentation.
"""

from forgemind.self_audit.audit import (
    Finding,
    FindingSeverity,
    SelfAuditReport,
    run_self_audit,
    scan_for_privacy_leaks,
)

__all__ = [
    "Finding",
    "FindingSeverity",
    "SelfAuditReport",
    "run_self_audit",
    "scan_for_privacy_leaks",
]
