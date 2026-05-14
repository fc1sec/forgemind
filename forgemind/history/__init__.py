"""Persistent calibration history — memory across consult sessions.

The history store is the consultant's memory: after each successful
`forgemind consult`, the chosen discipline / domain / variant is appended
to a local JSONL file so future sessions can suggest the same choice for
similar projects.

Storage is LOCAL ONLY (no network, no telemetry). The path defaults to
`~/.forgemind/history.jsonl` and can be overridden by the FORGEMIND_HISTORY_PATH
environment variable (used by tests).
"""

from .store import (
    DEFAULT_HISTORY_PATH_ENV,
    HistoryEntry,
    HistoryStore,
    get_default_history_path,
)

__all__ = [
    "DEFAULT_HISTORY_PATH_ENV",
    "HistoryEntry",
    "HistoryStore",
    "get_default_history_path",
]
