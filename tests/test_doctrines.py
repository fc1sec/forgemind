"""Tests for the doctrines registry (v1.3.0)."""

from __future__ import annotations

import pytest

from forgemind.doctrines import (
    DoctrineCategory,
    DoctrineRegistry,
    get_doctrine_registry,
)


@pytest.fixture(scope="module")
def registry() -> DoctrineRegistry:
    return get_doctrine_registry()


def test_registry_loads(registry: DoctrineRegistry):
    assert registry.version
    assert registry.last_updated
    assert len(registry.list_all()) >= 11


def test_constitutional_doctrines_present(registry: DoctrineRegistry):
    """The 5 constitutional doctrines from CertOS-SAGA capa 39-45 are present."""
    expected_short_ids = {"D39", "D40", "D41", "D43", "D45"}
    constitutional = registry.list_by_category(DoctrineCategory.CONSTITUTIONAL)
    short_ids = {d.short_id for d in constitutional}
    assert expected_short_ids.issubset(short_ids), (
        f"Missing constitutional doctrines: {expected_short_ids - short_ids}"
    )


def test_operational_doctrines_present(registry: DoctrineRegistry):
    expected_short_ids = {"D06", "D17", "D22", "D37", "D38"}
    operational = registry.list_by_category(DoctrineCategory.OPERATIONAL)
    short_ids = {d.short_id for d in operational}
    assert expected_short_ids.issubset(short_ids)


def test_methodological_doctrines_present(registry: DoctrineRegistry):
    expected_short_ids = {"D02", "D05"}
    methodological = registry.list_by_category(DoctrineCategory.METHODOLOGICAL)
    short_ids = {d.short_id for d in methodological}
    assert expected_short_ids.issubset(short_ids)


def test_lookup_by_short_id(registry: DoctrineRegistry):
    d = registry.get("D41")
    assert d is not None
    assert d.id == "capability_thresholds"
    assert d.category == DoctrineCategory.CONSTITUTIONAL


def test_lookup_by_long_id(registry: DoctrineRegistry):
    d = registry.get("aiia_pre_deployment")
    assert d is not None
    assert d.short_id == "D40"


def test_lookup_case_insensitive_short(registry: DoctrineRegistry):
    assert registry.get("d41") is not None
    assert registry.get("D41") is not None


def test_unknown_doctrine_returns_none(registry: DoctrineRegistry):
    assert registry.get("nonexistent_doctrine_xyz") is None


def test_every_doctrine_has_source_attribution(registry: DoctrineRegistry):
    """Anti-hallucination invariant: ForgeMind never invents a doctrine."""
    for d in registry.list_all():
        assert d.source.repo or d.source.url, (
            f"Doctrine {d.short_id} has no source attribution"
        )


def test_every_doctrine_has_normative_anchors(registry: DoctrineRegistry):
    """A doctrine without normative anchors is folklore, not policy."""
    for d in registry.list_all():
        assert len(d.normative_anchors) >= 1, (
            f"Doctrine {d.short_id} has no normative anchors"
        )


def test_certos_saga_repo_is_cited(registry: DoctrineRegistry):
    """Verify the upstream corpus is properly attributed across the registry."""
    certos_doctrines = [
        d for d in registry.list_all() if d.source.repo == "fc1sec/CertOS-SAGA"
    ]
    # All 11 first-cohort doctrines come from CertOS-SAGA
    assert len(certos_doctrines) >= 11
