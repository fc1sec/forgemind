"""Doctrines loader and typed API.

Loads `forgemind/data/doctrines.yaml` into a typed structure that
generators and the CLI can query. The registry is the single source of
truth for which named doctrines ForgeMind cites in its outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

import yaml


class DoctrineCategory(str, Enum):
    CONSTITUTIONAL = "constitutional"
    OPERATIONAL = "operational"
    METHODOLOGICAL = "methodological"


@dataclass(frozen=True)
class DoctrineSource:
    """Provenance for a doctrine — the upstream corpus it came from."""

    repo: str | None = None
    path: str | None = None
    url: str | None = None
    license_note: str | None = None


@dataclass(frozen=True)
class Doctrine:
    """A single named, citable doctrine."""

    id: str
    short_id: str
    name: str
    category: DoctrineCategory
    purpose: str
    summary: str
    when_to_cite: tuple[str, ...]
    normative_anchors: tuple[str, ...]
    source: DoctrineSource


class DoctrineRegistry:
    """Typed accessor over the doctrines.yaml registry."""

    def __init__(
        self,
        doctrines: dict[str, Doctrine],
        version: str,
        last_updated: str,
    ) -> None:
        self._doctrines = doctrines
        self.version = version
        self.last_updated = last_updated

    @property
    def doctrines(self) -> dict[str, Doctrine]:
        return dict(self._doctrines)

    def get(self, doctrine_id: str) -> Doctrine | None:
        """Look up a doctrine by full id or short id (e.g. 'D41')."""
        if doctrine_id in self._doctrines:
            return self._doctrines[doctrine_id]
        # short_id fallback (case-insensitive)
        target = doctrine_id.upper()
        for d in self._doctrines.values():
            if d.short_id.upper() == target:
                return d
        return None

    def list_by_category(self, category: DoctrineCategory) -> list[Doctrine]:
        return sorted(
            (d for d in self._doctrines.values() if d.category == category),
            key=lambda d: d.short_id,
        )

    def list_all(self) -> list[Doctrine]:
        return sorted(self._doctrines.values(), key=lambda d: d.short_id)


def _parse_source(raw: dict | None) -> DoctrineSource:
    if not raw:
        return DoctrineSource()
    return DoctrineSource(
        repo=raw.get("repo"),
        path=raw.get("path"),
        url=raw.get("url"),
        license_note=raw.get("license_note"),
    )


def _parse_doctrine(doctrine_id: str, raw: dict) -> Doctrine:
    return Doctrine(
        id=raw.get("id", doctrine_id),
        short_id=raw["short_id"],
        name=raw["name"],
        category=DoctrineCategory(raw["category"]),
        purpose=raw.get("purpose", "").strip(),
        summary=raw.get("summary", "").strip(),
        when_to_cite=tuple(raw.get("when_to_cite", []) or []),
        normative_anchors=tuple(raw.get("normative_anchors", []) or []),
        source=_parse_source(raw.get("source")),
    )


@lru_cache(maxsize=1)
def _default_data_path() -> Path:
    return Path(__file__).parent.parent / "data" / "doctrines.yaml"


def load_doctrine_registry(path: Path | None = None) -> DoctrineRegistry:
    """Load and parse the doctrines YAML file into a DoctrineRegistry."""
    yaml_path = path or _default_data_path()
    raw = yaml.safe_load(yaml_path.read_text())

    doctrines: dict[str, Doctrine] = {}
    for doctrine_id, doctrine_raw in (raw.get("doctrines") or {}).items():
        doctrines[doctrine_id] = _parse_doctrine(doctrine_id, doctrine_raw)

    return DoctrineRegistry(
        doctrines=doctrines,
        version=raw.get("version", "unknown"),
        last_updated=raw.get("last_updated", "unknown"),
    )


@lru_cache(maxsize=1)
def get_doctrine_registry() -> DoctrineRegistry:
    """Module-level singleton accessor (lru_cache keeps load cost off the hot path)."""
    return load_doctrine_registry()
