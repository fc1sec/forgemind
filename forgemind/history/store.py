"""Append-only history store for consultant calibrations.

Design choices:
  - JSONL on disk (append-only, easy to inspect, robust to crashes mid-write).
  - Local file only — no network, no telemetry, no cloud sync.
  - Path overridable via `FORGEMIND_HISTORY_PATH` env var so tests can
    redirect to a temp directory without monkey-patching.
  - Schema is intentionally narrow: identifiers + timestamp only. We do NOT
    store project content, only what was chosen and when.

A future version may add summarization, but for v1 the contract is:
  "I remember which variant you picked the last time you worked on this
   discipline+domain, so I can suggest it again."
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HISTORY_PATH_ENV = "FORGEMIND_HISTORY_PATH"


def get_default_history_path() -> Path:
    """Resolve the default history file path.

    Resolution order:
      1. FORGEMIND_HISTORY_PATH env var (if set and non-empty)
      2. ~/.forgemind/history.jsonl
    """
    override = os.environ.get(DEFAULT_HISTORY_PATH_ENV)
    if override:
        return Path(override).expanduser()
    return Path.home() / ".forgemind" / "history.jsonl"


@dataclass(frozen=True)
class HistoryEntry:
    """One recorded consultant calibration."""

    timestamp: str          # ISO-8601 UTC string
    project_slug: str       # the project's stable slug
    project_file: str       # absolute path of the project markdown
    taxonomy_version: str   # which taxonomy version was active
    discipline_id: str | None = None
    domain_id: str | None = None
    variant_id: str | None = None

    @classmethod
    def make(
        cls,
        project_slug: str,
        project_file: str,
        taxonomy_version: str,
        discipline_id: str | None,
        domain_id: str | None,
        variant_id: str | None,
    ) -> HistoryEntry:
        """Convenience factory that stamps the current UTC time."""
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            project_slug=project_slug,
            project_file=project_file,
            taxonomy_version=taxonomy_version,
            discipline_id=discipline_id,
            domain_id=domain_id,
            variant_id=variant_id,
        )


class HistoryStore:
    """Append-only JSONL store of HistoryEntry records."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path else get_default_history_path()

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def append(self, entry: HistoryEntry) -> None:
        """Append a single entry. Creates parent dirs as needed.

        Failures here are non-fatal for the caller — losing a history line
        should never block output generation. We swallow IO errors silently
        but keep the store API explicit for tests that DO care.
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
        except OSError:
            # Non-fatal: the consultant must keep working even if disk is full
            # or the directory is read-only. Tests using explicit paths and
            # writable dirs will not hit this branch.
            pass

    def clear(self) -> None:
        """Erase the history file (no-op if it doesn't exist)."""
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def all_entries(self) -> list[HistoryEntry]:
        """Return all entries in append order. Empty list if file missing."""
        if not self.path.exists():
            return []
        entries: list[HistoryEntry] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    # Skip corrupt lines; never raise on read so a malformed
                    # entry can't break the consultant.
                    continue
                entries.append(
                    HistoryEntry(
                        timestamp=str(data.get("timestamp", "")),
                        project_slug=str(data.get("project_slug", "")),
                        project_file=str(data.get("project_file", "")),
                        taxonomy_version=str(data.get("taxonomy_version", "")),
                        discipline_id=data.get("discipline_id"),
                        domain_id=data.get("domain_id"),
                        variant_id=data.get("variant_id"),
                    )
                )
        return entries

    # ------------------------------------------------------------------
    # Suggestion queries — used by the consultant to bias defaults
    # ------------------------------------------------------------------

    def recent_for_domain(
        self, domain_id: str, limit: int = 10
    ) -> list[HistoryEntry]:
        """Return up to `limit` most-recent entries matching a domain."""
        matches = [e for e in self.all_entries() if e.domain_id == domain_id]
        return matches[-limit:][::-1]  # reverse so most recent first

    def suggest_variant_for_domain(self, domain_id: str) -> str | None:
        """Return the most-recently-chosen variant id for a domain, or None."""
        matches = self.recent_for_domain(domain_id, limit=1)
        if not matches:
            return None
        return matches[0].variant_id

    def suggest_domain_for_discipline(self, discipline_id: str) -> str | None:
        """Return the most-recently-chosen domain id within a discipline."""
        matches = [
            e
            for e in self.all_entries()
            if e.discipline_id == discipline_id and e.domain_id
        ]
        if not matches:
            return None
        return matches[-1].domain_id

    def most_recent_discipline(self) -> str | None:
        """Most-recent discipline id across all entries, or None."""
        entries = self.all_entries()
        for entry in reversed(entries):
            if entry.discipline_id:
                return entry.discipline_id
        return None

    def is_empty(self) -> bool:
        return not self.all_entries()

    # ------------------------------------------------------------------
    # Convenience iter (lets callers stream without loading list twice)
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterable[HistoryEntry]:
        return iter(self.all_entries())
