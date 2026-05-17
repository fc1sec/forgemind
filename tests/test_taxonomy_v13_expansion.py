"""Tests for the v1.3.0 taxonomy expansion (multi-norm Annex SL + new domains)."""

from __future__ import annotations

import pytest

from forgemind.disciplines import Coverage, get_taxonomy


@pytest.fixture(scope="module")
def taxonomy():
    return get_taxonomy()


# ---------------------------------------------------------------------------
# Multi-norm Annex SL upgrade — domains promoted from not_covered to partial
# ---------------------------------------------------------------------------

PROMOTED_TO_PARTIAL = [
    "iso13485",
    "iso14001",
    "iso45001",
    "iso27001",
    "iso42001",
    "iso22301",
]


@pytest.mark.parametrize("domain_id", PROMOTED_TO_PARTIAL)
def test_multi_norm_domain_is_now_partial(taxonomy, domain_id):
    domain = taxonomy.get_domain(domain_id)
    assert domain is not None, f"Domain {domain_id} missing from taxonomy"
    assert domain.coverage == Coverage.PARTIAL


@pytest.mark.parametrize("domain_id", PROMOTED_TO_PARTIAL)
def test_multi_norm_domain_has_hls_variant(taxonomy, domain_id):
    domain = taxonomy.get_domain(domain_id)
    assert domain is not None
    variant_ids = {v.id for v in domain.variants}
    assert "hls_annex_sl_clause_map" in variant_ids


@pytest.mark.parametrize("domain_id", PROMOTED_TO_PARTIAL)
def test_multi_norm_domain_has_boundary_conditions(taxonomy, domain_id):
    """Honest disclosure: every newly-promoted domain MUST list what's NOT covered."""
    domain = taxonomy.get_domain(domain_id)
    assert domain is not None
    assert len(domain.boundary_conditions) >= 1


@pytest.mark.parametrize("domain_id", PROMOTED_TO_PARTIAL)
def test_multi_norm_domain_cites_certos_saga(taxonomy, domain_id):
    """Every new HLS variant should attribute the upstream source."""
    domain = taxonomy.get_domain(domain_id)
    assert domain is not None
    hls = next((v for v in domain.variants if v.id == "hls_annex_sl_clause_map"), None)
    assert hls is not None
    # Source must mention CertOS-SAGA (the doctrinal corpus we're drawing from)
    assert hls.source and "CertOS-SAGA" in hls.source


# ---------------------------------------------------------------------------
# New domains
# ---------------------------------------------------------------------------

def test_pokayoke_patterns_domain_present(taxonomy):
    d = taxonomy.get_domain("pokayoke_patterns")
    assert d is not None
    assert d.coverage == Coverage.PARTIAL
    variant_ids = {v.id for v in d.variants}
    assert "pokayoke_10_type_taxonomy" in variant_ids


def test_agnostic_task_routing_domain_present(taxonomy):
    d = taxonomy.get_domain("agnostic_task_routing")
    assert d is not None
    assert d.coverage == Coverage.PARTIAL
    variant_ids = {v.id for v in d.variants}
    assert "seven_tier_decision_hierarchy" in variant_ids


# ---------------------------------------------------------------------------
# Honest-disclosure invariants
# ---------------------------------------------------------------------------

def test_iso13485_still_escalates_for_design_controls(taxonomy):
    """We promoted ISO 13485 to partial but must still escalate for design controls."""
    d = taxonomy.get_domain("iso13485")
    assert d is not None
    boundary_text = " ".join(d.boundary_conditions).lower()
    # The specialised bits NOT covered must be explicit
    assert "design controls" in boundary_text or "iso 14971" in boundary_text
    assert d.escalate_to and "regulatory" in d.escalate_to.lower()


def test_iso27001_still_escalates_for_annex_a(taxonomy):
    d = taxonomy.get_domain("iso27001")
    assert d is not None
    boundary_text = " ".join(d.boundary_conditions).lower()
    assert "annex a" in boundary_text or "statement of applicability" in boundary_text


def test_iso42001_anchors_to_d45(taxonomy):
    """ISO/IEC 42001 partial coverage cites the AIMS-integrated-SGC doctrine."""
    d = taxonomy.get_domain("iso42001")
    assert d is not None
    hls = next((v for v in d.variants if v.id == "hls_annex_sl_clause_map"), None)
    assert hls is not None
    # Source should mention D45 (the integration doctrine)
    assert "45" in (hls.source or "")


def test_as9100_remains_not_covered(taxonomy):
    """AS9100 has aerospace-specific concerns beyond the HLS skeleton; still not_covered."""
    d = taxonomy.get_domain("as9100")
    assert d is not None
    assert d.coverage == Coverage.NOT_COVERED
