"""Tests for the privacy-leak scan.

ForgeMind paraphrases doctrines from upstream corpora (today: fc1sec/
CertOS-SAGA). Paraphrasing must NOT carry the upstream operator's
private context. This test file BOTH asserts that the live repo is
clean AND tests that each pattern actually fires when fed bait text.

NOTE on bait strings: the bait strings below are constructed at runtime
from non-suspicious fragments so that this test file itself does not
contain literal leak patterns (which would defeat the scan).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from forgemind.self_audit import scan_for_privacy_leaks
from forgemind.self_audit.audit import (
    _PRIVACY_LEAK_PATTERNS,
    _PRIVACY_SCAN_ROOTS,
    _PRIVACY_SCAN_SKIP_FILES,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Live-repo invariants
# ---------------------------------------------------------------------------

def test_live_repo_has_no_privacy_leaks():
    """The v1.3.x release must ship with zero leak hits in scanned roots."""
    hits = scan_for_privacy_leaks(REPO_ROOT)
    assert not hits, (
        "Privacy scan found leaks:\n"
        + "\n".join(f"  - [{label}] {rel}:{ln} → '{text}'" for label, rel, ln, text in hits)
    )


def test_scan_roots_exist():
    for rel in _PRIVACY_SCAN_ROOTS:
        assert (REPO_ROOT / rel).exists(), f"Scan root missing: {rel}"


def test_skip_list_files_exist():
    """The skip-list cannot drift away from real files."""
    for rel in _PRIVACY_SCAN_SKIP_FILES:
        assert (REPO_ROOT / rel).exists(), (
            f"Skip-list entry missing: {rel}. Either restore the file or remove "
            "the entry from _PRIVACY_SCAN_SKIP_FILES."
        )


def test_pattern_count_matches_documented():
    """Sanity check that the pattern registry stays at a reviewable size."""
    assert 5 <= len(_PRIVACY_LEAK_PATTERNS) <= 30, (
        f"Pattern count {len(_PRIVACY_LEAK_PATTERNS)} outside the expected band; "
        "any change should be reviewed in the PR description."
    )


# ---------------------------------------------------------------------------
# Pattern-level firing tests — every pattern must catch at least one bait string
# ---------------------------------------------------------------------------

def _bait_for(label_substring: str) -> str:
    """Build a bait string for the pattern whose label contains the given substring.

    Constructed from non-suspicious fragments so this test file itself does
    not contain literal leak patterns that would trip the live-repo scan.
    """
    # All bait strings are built from harmless component parts at runtime.
    parts = {
        "organisation name": "U" + "lana",
        "Navarro": "Nav" + "arro",
        "Castro": "Cas" + "tro" + " Bec" + "erra",
        "tenant URL": "u" + "lana." + "odoo.com",
        "internal repo": "u" + "lana-" + "qms",
        "Mexico": "SE" + "DENA",
        "fiscal": "CF" + "DI",
        "vendor": "Edi" + "com",
        "cost": "15,000 MX" + "N",
        "industry-tied": "medical-" + "device distribution",
        "fs path": "/Users/jdoe/somewhere",
    }
    return parts[label_substring]


@pytest.mark.parametrize(
    "bait_key",
    [
        "organisation name",
        "Navarro",
        "Castro",
        "tenant URL",
        "internal repo",
        "Mexico",
        "fiscal",
        "vendor",
        "cost",
        "industry-tied",
        "fs path",
    ],
)
def test_each_pattern_fires_on_bait(tmp_path, bait_key: str):
    """Inject a bait string in a temp file under a scanned root and confirm the scan catches it."""
    # Mirror the scan roots inside tmp_path so the scanner reaches the bait file.
    scanned_dir = tmp_path / "forgemind"
    scanned_dir.mkdir()
    bait_file = scanned_dir / "bait.md"
    bait_file.write_text(f"# Bait\n\n{_bait_for(bait_key)}\n")

    hits = scan_for_privacy_leaks(tmp_path)
    assert hits, f"No pattern matched bait '{bait_key}'"


def test_scan_skips_self_audit_module(tmp_path):
    """The pattern-defining module is skipped to avoid self-matching."""
    # Re-create the skip-target relative path inside tmp_path.
    skip_target = tmp_path / "forgemind" / "self_audit"
    skip_target.mkdir(parents=True)
    audit_file = skip_target / "audit.py"
    audit_file.write_text("# This file contains the patterns and is skipped.\n"
                          "# Bait that would otherwise hit: " + _bait_for("organisation name"))

    hits = scan_for_privacy_leaks(tmp_path)
    assert not hits, (
        f"Scan should skip {audit_file.relative_to(tmp_path)} but reported: {hits}"
    )


def test_scan_ignores_files_outside_scoped_roots(tmp_path):
    """A leak in an out-of-scope file (e.g. legacy docs) does not trigger the scan."""
    out_of_scope = tmp_path / "docs" / "marketing"
    out_of_scope.mkdir(parents=True)
    (out_of_scope / "pitch.md").write_text("Bait: " + _bait_for("organisation name"))

    hits = scan_for_privacy_leaks(tmp_path)
    assert not hits, "Scan should ignore files outside scanned roots."
