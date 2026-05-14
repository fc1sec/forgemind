"""ForgeMind disciplines taxonomy — the meta-knowledge of what ForgeMind knows.

This package is ForgeMind's self-knowledge: the declarative answer to
"What can ForgeMind advise on, and what does it know it cannot?"
"""

from .taxonomy import (
    Coverage,
    Discipline,
    DisciplineTaxonomy,
    Domain,
    OutOfScopeEntry,
    Variant,
    get_taxonomy,
)

__all__ = [
    "Coverage",
    "Discipline",
    "DisciplineTaxonomy",
    "Domain",
    "OutOfScopeEntry",
    "Variant",
    "get_taxonomy",
]
