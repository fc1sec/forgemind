"""Version management and compatibility tracking for ForgeMind."""

__version__ = "1.3.0"

# Breaking changes documentation per major version
BREAKING_CHANGES = {
    "2.0.0": [
        "BREAKING: ProjectAnalysis schema updated (new 'governance' field required)",
        "BREAKING: Decision log format changed (see BREAKING_CHANGES.md)",
        "Removed: old 'legacy_format' parameter from generators",
        "Migration: Run 'forgemind migrate --from 1.2.x --to 2.0.0' to upgrade projects",
    ],
    "1.3.0": [],  # No breaking changes from 1.2.x; adds outputs + doctrines registry
    "1.2.0": [],  # No breaking changes from 1.1
    "1.1.0": [],  # No breaking changes from 1.0
}

# Compatibility matrix: which versions work together
COMPATIBILITY = {
    "1.3.0": {
        "works_with_projects": ["1.3.0", "1.2.1", "1.2.0", "1.1.0"],
        "works_with_outputs": ["1.3.0", "1.2.1", "1.2.0", "1.1.0"],
        "can_rollback_to": ["1.2.1", "1.2.0", "1.1.0"],
        "backward_compatible": True,
    },
    "1.2.1": {
        "works_with_projects": ["1.2.1", "1.2.0", "1.1.0"],
        "works_with_outputs": ["1.2.1", "1.2.0", "1.1.0"],
        "can_rollback_to": ["1.2.0", "1.1.0"],
        "backward_compatible": True,
    },
    "1.2.0": {
        "works_with_projects": ["1.2.0", "1.1.0"],
        "works_with_outputs": ["1.2.0", "1.1.0"],
        "can_rollback_to": ["1.1.0"],
        "backward_compatible": True,
    },
    "1.1.0": {
        "works_with_projects": ["1.1.0", "1.0.0"],
        "works_with_outputs": ["1.1.0"],
        "can_rollback_to": [],
        "backward_compatible": False,  # Breaking from 1.0
    },
}

RELEASE_NOTES = {
    "1.3.0": """
## v1.3.0: Constitutional Governance Release

**What's New:**
- ✅ Doctrines registry (`forgemind/data/doctrines.yaml`) — 11 named, citable
  doctrines anchored in CertOS-SAGA (constitutional, operational, methodological)
- ✅ New CLI: `forgemind doctrines [list|show] [--category]`
- ✅ Multi-norm Annex SL coverage upgraded — ISO 13485, ISO 14001, ISO 45001,
  ISO/IEC 27001, ISO/IEC 42001, ISO 22301 move from `not_covered` to `partial`
  with HLS clause-map variants and honest boundary conditions
- ✅ New domain: `pokayoke_patterns` (10-type mistake-proofing taxonomy)
- ✅ New domain: `agnostic_task_routing` (7-tier decision hierarchy)
- ✅ 5 new output artefacts:
    · EVIDENCE_SCORING.md     (universal · D17 + D37)
    · TOKEN_COST_GOVERNANCE.md (universal · D22 + D06)
    · AIIA_PRE_DEPLOYMENT.md  (AI/ML domains · D40)
    · CAPABILITY_THRESHOLDS.md (AI/ML domains · D41)
    · SKILL_CARD.md           (AI/ML domains · D43)
- ✅ Every new output cites its anchoring doctrine inline with the upstream URL

**Backward Compatibility:**
- v1.2.x projects: work unchanged
- v1.1.0 projects: work unchanged
- Output count grows from 17 → 19 (universal) or 22 (AI/ML domains)
- No CLI breaking changes; `doctrines` is purely additive

**Sources:**
- All new doctrines drawn from `fc1sec/CertOS-SAGA` (see ATTRIBUTIONS.md
  and `forgemind doctrines` for per-entry citations).
""",
    "1.2.1": """
## v1.2.1: Safe Updates Release

**What's New:**
- ✅ Version detection and update notifications
- ✅ Backward compatibility guarantee system
- ✅ Safe upgrade/rollback paths documented
- ✅ Compatibility matrix per version

**Safety Guarantees:**
- ✅ No breaking changes from v1.2.0
- ✅ All v1.1.0 projects work unchanged
- ✅ Automatic version checks (non-blocking)
- ✅ Clear migration paths for major updates

**Backward Compatibility:**
- v1.2.0 projects: ✅ Work perfectly with v1.2.1
- v1.1.0 projects: ✅ Work perfectly with v1.2.1
- Rollback: `pip install forgemind==1.2.0` (anytime, safe)

**Upgrade Path:**
```bash
pip install --upgrade forgemind
# Your projects continue to work without any changes
```

See UPDATES_AND_SAFETY.md for detailed safety information.
""",
    "1.2.0": """
## v1.2.0: Reverse Patterns Release

**What's New:**
- ✅ Plugin architecture for domain-specific reversal patterns
- ✅ Built-in patterns: ISO 9001, Software, AI/ML
- ✅ ReverseContextGenerator for automatic reversal planning
- ✅ EpistemicValidator to prevent hallucination
- ✅ Community contribution guide for new patterns

**Backward Compatibility:**
- ✅ All v1.1.0 projects work unchanged
- ✅ New reversal plans auto-added when domain supported
- ✅ Graceful escalation for unsupported domains
- ✅ No API changes to existing generators

See V1.2.0_COMPLETION_SUMMARY.md for full details.
""",
}


def get_has_breaking_changes(from_version: str, to_version: str) -> bool:
    """Check if upgrade from one version to another includes breaking changes."""
    try:
        from packaging import version
        from_major = version.parse(from_version).major
        to_major = version.parse(to_version).major
        return to_major > from_major
    except Exception:
        return False


def is_compatible(installed_version: str, project_version: str) -> bool:
    """Check if installed version can read projects from a different version."""
    if installed_version not in COMPATIBILITY:
        return True  # Unknown version, assume compatible

    compat = COMPATIBILITY[installed_version]
    return project_version in compat.get("works_with_projects", [])
