"""Disciplines taxonomy loader and typed API.

Loads `forgemind/data/disciplines.yaml` into a typed, queryable structure that
the rest of ForgeMind can use to decide whether to advise, label outputs with
confidence, or escalate to a human expert.

The taxonomy is the SINGLE SOURCE OF TRUTH for coverage claims. The test suite
verifies that every covered/partial domain has a corresponding plugin or
generator, preventing the codebase from claiming expertise it does not have.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

import yaml


class Coverage(str, Enum):
    """How well ForgeMind covers a domain."""

    COVERED = "covered"
    PARTIAL = "partial"
    NOT_COVERED = "not_covered"


@dataclass(frozen=True)
class Variant:
    """A single validated pattern within a domain."""

    id: str
    name: str
    source: str | None = None
    url: str | None = None
    license: str | None = None
    confidence: float = 0.5
    production_validated: bool = False
    since: str | None = None
    scope_evidence: str | None = None
    # Decision-support fields (used by `forgemind compare-variants` and the
    # consultant's variant comparison step). Optional — variants without them
    # render the comparison view with "no criteria documented" placeholders.
    when_to_choose: tuple[str, ...] = ()
    pros: tuple[str, ...] = ()
    cons: tuple[str, ...] = ()


@dataclass(frozen=True)
class Domain:
    """A domain of expertise within a discipline."""

    id: str
    discipline_id: str
    name: str
    coverage: Coverage
    confidence: float | None = None
    variants: tuple[Variant, ...] = ()
    boundary_conditions: tuple[str, ...] = ()
    escalate_to: str | None = None
    reason: str | None = None  # populated when not_covered

    def is_actionable(self) -> bool:
        """True if ForgeMind can produce advice in this domain (covered or partial)."""
        return self.coverage in (Coverage.COVERED, Coverage.PARTIAL)


@dataclass(frozen=True)
class Discipline:
    """A top-level field of expertise."""

    id: str
    name: str
    description: str
    domains: dict[str, Domain]


@dataclass(frozen=True)
class OutOfScopeEntry:
    """A discipline ForgeMind explicitly refuses to advise on."""

    id: str
    reason: str
    escalate_to: str
    rationale: str


class DisciplineTaxonomy:
    """Typed accessor over the disciplines.yaml taxonomy."""

    def __init__(
        self,
        disciplines: dict[str, Discipline],
        out_of_scope: dict[str, OutOfScopeEntry],
        version: str,
        last_updated: str,
        coverage_legend: dict[str, str],
    ) -> None:
        self._disciplines = disciplines
        self._out_of_scope = out_of_scope
        self.version = version
        self.last_updated = last_updated
        self.coverage_legend = coverage_legend
        # Index domains by id for fast lookup
        self._domain_index: dict[str, Domain] = {
            domain_id: domain
            for discipline in disciplines.values()
            for domain_id, domain in discipline.domains.items()
        }

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @property
    def disciplines(self) -> dict[str, Discipline]:
        """All disciplines, keyed by id."""
        return dict(self._disciplines)

    @property
    def out_of_scope(self) -> dict[str, OutOfScopeEntry]:
        """Disciplines explicitly out of scope by design."""
        return dict(self._out_of_scope)

    def get_discipline(self, discipline_id: str) -> Discipline | None:
        return self._disciplines.get(discipline_id)

    def get_domain(self, domain_id: str) -> Domain | None:
        """Get a domain by id (across all disciplines)."""
        return self._domain_index.get(domain_id)

    # ------------------------------------------------------------------
    # Coverage queries — the questions other modules ask
    # ------------------------------------------------------------------

    def coverage_for(self, domain_id: str) -> Coverage:
        """Return the coverage level for a domain. NOT_COVERED if unknown."""
        domain = self._domain_index.get(domain_id)
        if domain is None:
            return Coverage.NOT_COVERED
        return domain.coverage

    def can_advise_on(self, domain_id: str) -> bool:
        """True if ForgeMind has at least partial coverage for this domain."""
        return self.coverage_for(domain_id) in (Coverage.COVERED, Coverage.PARTIAL)

    def must_escalate(self, domain_id: str) -> bool:
        """True if ForgeMind must escalate (no coverage, or out of scope by design)."""
        if domain_id in self._out_of_scope:
            return True
        return self.coverage_for(domain_id) == Coverage.NOT_COVERED

    def escalation_contact(self, domain_id: str) -> str:
        """Suggest who to escalate to for this domain."""
        if domain_id in self._out_of_scope:
            return self._out_of_scope[domain_id].escalate_to
        domain = self._domain_index.get(domain_id)
        if domain and domain.escalate_to:
            return domain.escalate_to
        return "Domain expert"

    def confidence_for(self, domain_id: str) -> float:
        """Return the calibrated confidence for advice in this domain (0.0–1.0)."""
        domain = self._domain_index.get(domain_id)
        if domain is None:
            return 0.0
        if domain.confidence is not None:
            return domain.confidence
        # Fall back to highest variant confidence
        if domain.variants:
            return max(v.confidence for v in domain.variants)
        return 0.0

    def boundary_conditions(self, domain_id: str) -> tuple[str, ...]:
        """Known gaps/limitations within a covered or partial domain."""
        domain = self._domain_index.get(domain_id)
        if domain is None:
            return ()
        return domain.boundary_conditions

    # ------------------------------------------------------------------
    # Listing helpers (used by `forgemind capabilities` and reports)
    # ------------------------------------------------------------------

    def list_by_coverage(self, coverage: Coverage) -> list[Domain]:
        """All domains at a given coverage level, sorted by name."""
        return sorted(
            (d for d in self._domain_index.values() if d.coverage == coverage),
            key=lambda d: d.name,
        )

    def list_covered(self) -> list[Domain]:
        return self.list_by_coverage(Coverage.COVERED)

    def list_partial(self) -> list[Domain]:
        return self.list_by_coverage(Coverage.PARTIAL)

    def list_not_covered(self) -> list[Domain]:
        return self.list_by_coverage(Coverage.NOT_COVERED)

    def list_out_of_scope(self) -> list[OutOfScopeEntry]:
        return sorted(self._out_of_scope.values(), key=lambda e: e.id)

    def summary(self) -> dict[str, int]:
        """Quick coverage summary for reporting."""
        return {
            "disciplines": len(self._disciplines),
            "domains_total": len(self._domain_index),
            "covered": len(self.list_covered()),
            "partial": len(self.list_partial()),
            "not_covered": len(self.list_not_covered()),
            "out_of_scope_by_design": len(self._out_of_scope),
        }


# ----------------------------------------------------------------------
# Loader
# ----------------------------------------------------------------------


def _default_yaml_path() -> Path:
    """Path to the bundled disciplines.yaml."""
    return Path(__file__).parent.parent / "data" / "disciplines.yaml"


def load_taxonomy(yaml_path: Path | None = None) -> DisciplineTaxonomy:
    """Load and parse the disciplines taxonomy from YAML.

    Args:
        yaml_path: Optional override path. Defaults to the bundled file.

    Raises:
        FileNotFoundError: if the YAML file is missing.
        ValueError: if the YAML is malformed or violates the schema.
    """
    path = yaml_path or _default_yaml_path()
    if not path.exists():
        raise FileNotFoundError(f"Disciplines taxonomy not found at {path}")

    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if not isinstance(raw, dict):
        raise ValueError("disciplines.yaml must contain a mapping at the root")

    version = str(raw.get("version", "0.0"))
    last_updated = str(raw.get("last_updated", ""))
    coverage_legend = dict(raw.get("coverage_legend", {}) or {})

    disciplines: dict[str, Discipline] = {}
    for discipline_id, discipline_data in (raw.get("disciplines") or {}).items():
        if not isinstance(discipline_data, dict):
            raise ValueError(f"Discipline '{discipline_id}' must be a mapping")
        domains: dict[str, Domain] = {}
        for domain_id, domain_data in (discipline_data.get("domains") or {}).items():
            domains[domain_id] = _parse_domain(domain_id, discipline_id, domain_data)
        disciplines[discipline_id] = Discipline(
            id=discipline_id,
            name=str(discipline_data.get("name", discipline_id)),
            description=str(discipline_data.get("description", "")).strip(),
            domains=domains,
        )

    out_of_scope: dict[str, OutOfScopeEntry] = {}
    for entry_id, entry_data in (raw.get("out_of_scope_by_design") or {}).items():
        if not isinstance(entry_data, dict):
            raise ValueError(f"Out-of-scope entry '{entry_id}' must be a mapping")
        out_of_scope[entry_id] = OutOfScopeEntry(
            id=entry_id,
            reason=str(entry_data.get("reason", "")).strip(),
            escalate_to=str(entry_data.get("escalate_to", "Domain expert")).strip(),
            rationale=str(entry_data.get("rationale", "")).strip(),
        )

    return DisciplineTaxonomy(
        disciplines=disciplines,
        out_of_scope=out_of_scope,
        version=version,
        last_updated=last_updated,
        coverage_legend=coverage_legend,
    )


def _parse_domain(domain_id: str, discipline_id: str, data: dict) -> Domain:
    """Parse a single domain entry from YAML."""
    coverage_raw = data.get("coverage")
    if coverage_raw not in {c.value for c in Coverage}:
        raise ValueError(
            f"Domain '{domain_id}' has invalid coverage '{coverage_raw}'. "
            f"Expected one of: {[c.value for c in Coverage]}"
        )
    coverage = Coverage(coverage_raw)

    variants_data = data.get("variants") or []
    variants = tuple(
        Variant(
            id=str(v["id"]),
            name=str(v.get("name", v["id"])),
            source=v.get("source"),
            url=v.get("url"),
            license=v.get("license"),
            confidence=float(v.get("confidence", 0.5)),
            production_validated=bool(v.get("production_validated", False)),
            since=v.get("since"),
            scope_evidence=v.get("scope_evidence"),
            when_to_choose=tuple(str(x) for x in (v.get("when_to_choose") or [])),
            pros=tuple(str(x) for x in (v.get("pros") or [])),
            cons=tuple(str(x) for x in (v.get("cons") or [])),
        )
        for v in variants_data
    )

    boundary_conditions = tuple(
        str(item) for item in (data.get("boundary_conditions") or [])
    )

    return Domain(
        id=domain_id,
        discipline_id=discipline_id,
        name=str(data.get("name", domain_id)),
        coverage=coverage,
        confidence=(
            float(data["confidence"]) if data.get("confidence") is not None else None
        ),
        variants=variants,
        boundary_conditions=boundary_conditions,
        escalate_to=data.get("escalate_to"),
        reason=data.get("reason"),
    )


# ----------------------------------------------------------------------
# Convenience singleton (cached so repeated calls don't reparse YAML)
# ----------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_taxonomy() -> DisciplineTaxonomy:
    """Return the cached default taxonomy.

    Use `load_taxonomy(path)` directly if you need a custom YAML file or
    want to bypass caching (e.g. in tests).
    """
    return load_taxonomy()
