"""Constitutional & operational doctrines registry.

A typed, queryable accessor over `forgemind/data/doctrines.yaml`. Doctrines
are named, citable references — every entry is sourced from an external,
attributable corpus (today: fc1sec/CertOS-SAGA) and ForgeMind never
fabricates one.

Generators import this module to anchor their outputs in named doctrines
with full normative attribution.
"""

from forgemind.doctrines.registry import (
    Doctrine,
    DoctrineCategory,
    DoctrineRegistry,
    DoctrineSource,
    get_doctrine_registry,
)

__all__ = [
    "Doctrine",
    "DoctrineCategory",
    "DoctrineRegistry",
    "DoctrineSource",
    "get_doctrine_registry",
]
