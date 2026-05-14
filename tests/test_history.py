"""Tests for the persistent calibration history store.

Memory is the consultant's last skill: remember past calibration choices so
future sessions can suggest them as defaults. These tests cover:
  - Round-trip JSONL append/read
  - Suggestion queries (recent_for_domain, suggest_variant_for_domain etc.)
  - Integration with ConsultantSession (default_index biased by history)
  - CLI commands `forgemind history` and `forgemind history --clear`
  - Resilience: missing file, corrupt lines, env-var override
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from forgemind.cli.main import app
from forgemind.consultant import ConsultantSession
from forgemind.history import (
    DEFAULT_HISTORY_PATH_ENV,
    HistoryEntry,
    HistoryStore,
    get_default_history_path,
)

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def isolated_history(tmp_path: Path, monkeypatch):
    """Redirect the default history path to a temp file for the test session."""
    history_file = tmp_path / "history.jsonl"
    monkeypatch.setenv(DEFAULT_HISTORY_PATH_ENV, str(history_file))
    return history_file


@pytest.fixture
def qms_project(tmp_path: Path) -> Path:
    p = tmp_path / "qms.md"
    p.write_text(
        """# QMS Document Control Upgrade

## Objective
Implement ISO 9001:2015 document control for the quality management system.

## Context
Audit-ready process documentation with traceability.

## Scope
Document lifecycle, compliance, audit trail.

## Risks
Non-compliance during certification audit.

## Success Criteria
Pass external audit.
""",
        encoding="utf-8",
    )
    return p


# ----------------------------------------------------------------------
# Storage round-trip
# ----------------------------------------------------------------------


class TestHistoryStore:
    def test_default_path_respects_env_var(self, monkeypatch, tmp_path: Path):
        target = tmp_path / "alt.jsonl"
        monkeypatch.setenv(DEFAULT_HISTORY_PATH_ENV, str(target))
        assert get_default_history_path() == target

    def test_default_path_falls_back_to_home(self, monkeypatch):
        monkeypatch.delenv(DEFAULT_HISTORY_PATH_ENV, raising=False)
        p = get_default_history_path()
        assert ".forgemind" in p.parts
        assert p.name == "history.jsonl"

    def test_append_then_read(self, tmp_path: Path):
        path = tmp_path / "history.jsonl"
        store = HistoryStore(path=path)
        store.append(
            HistoryEntry.make(
                project_slug="alpha",
                project_file="/tmp/alpha.md",
                taxonomy_version="1.0",
                discipline_id="quality_management",
                domain_id="iso9001",
                variant_id="cespi_unlp_8state",
            )
        )
        entries = store.all_entries()
        assert len(entries) == 1
        assert entries[0].project_slug == "alpha"
        assert entries[0].domain_id == "iso9001"
        assert entries[0].variant_id == "cespi_unlp_8state"

    def test_append_is_jsonl(self, tmp_path: Path):
        path = tmp_path / "history.jsonl"
        store = HistoryStore(path=path)
        for slug in ("a", "b", "c"):
            store.append(
                HistoryEntry.make(
                    project_slug=slug,
                    project_file=f"/tmp/{slug}.md",
                    taxonomy_version="1.0",
                    discipline_id="quality_management",
                    domain_id="iso9001",
                    variant_id=None,
                )
            )
        # Each line is a valid JSON object
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3
        for line in lines:
            assert json.loads(line)["project_slug"] in {"a", "b", "c"}

    def test_clear_removes_file(self, tmp_path: Path):
        path = tmp_path / "history.jsonl"
        store = HistoryStore(path=path)
        store.append(
            HistoryEntry.make(
                project_slug="x",
                project_file="/tmp/x.md",
                taxonomy_version="1.0",
                discipline_id=None,
                domain_id=None,
                variant_id=None,
            )
        )
        assert path.exists()
        store.clear()
        assert not path.exists()
        assert store.all_entries() == []

    def test_missing_file_returns_empty(self, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "does_not_exist.jsonl")
        assert store.all_entries() == []
        assert store.is_empty()

    def test_corrupt_line_skipped(self, tmp_path: Path):
        path = tmp_path / "history.jsonl"
        path.write_text("not-valid-json\n", encoding="utf-8")
        store = HistoryStore(path=path)
        # Should NOT raise; the corrupt line is skipped silently.
        assert store.all_entries() == []


# ----------------------------------------------------------------------
# Suggestion queries
# ----------------------------------------------------------------------


class TestSuggestions:
    def _seed(self, path: Path, *entries: tuple[str, str, str, str]) -> HistoryStore:
        store = HistoryStore(path=path)
        for slug, disc, dom, var in entries:
            store.append(
                HistoryEntry.make(
                    project_slug=slug,
                    project_file=f"/tmp/{slug}.md",
                    taxonomy_version="1.0",
                    discipline_id=disc,
                    domain_id=dom,
                    variant_id=var,
                )
            )
        return store

    def test_suggest_variant_for_domain_returns_most_recent(self, tmp_path: Path):
        store = self._seed(
            tmp_path / "h.jsonl",
            ("a", "quality_management", "iso9001", "cespi_unlp_8state"),
            ("b", "quality_management", "iso9001", "iso9001_minimalist_5state"),
        )
        # Most-recent variant for iso9001 is minimalist
        assert store.suggest_variant_for_domain("iso9001") == "iso9001_minimalist_5state"

    def test_suggest_variant_for_unknown_domain_is_none(self, tmp_path: Path):
        store = self._seed(
            tmp_path / "h.jsonl",
            ("a", "quality_management", "iso9001", "cespi_unlp_8state"),
        )
        assert store.suggest_variant_for_domain("not_a_known_domain") is None

    def test_most_recent_discipline(self, tmp_path: Path):
        store = self._seed(
            tmp_path / "h.jsonl",
            ("a", "quality_management", "iso9001", "cespi_unlp_8state"),
            ("b", "software_engineering", "software", None),
        )
        assert store.most_recent_discipline() == "software_engineering"


# ----------------------------------------------------------------------
# Consultant integration — defaults are biased by history
# ----------------------------------------------------------------------


class TestConsultantUsesHistory:
    def test_variant_question_default_is_prior_choice(self, qms_project: Path, tmp_path: Path):
        store = HistoryStore(path=tmp_path / "h.jsonl")
        # Pretend the user previously picked the minimalist variant
        store.append(
            HistoryEntry.make(
                project_slug="prev",
                project_file="/tmp/prev.md",
                taxonomy_version="1.0",
                discipline_id="quality_management",
                domain_id="iso9001",
                variant_id="iso9001_minimalist_5state",
            )
        )

        session = ConsultantSession(qms_project, history=store)
        session.load_project()
        # Walk to the variant question
        session.answer(session.next_turn(), 0)  # discipline
        turn = session.next_turn()              # domain
        iso_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_idx)
        turn = session.next_turn()              # variant
        # The default option should now be the prior minimalist choice,
        # not the production-validated CeSPI default.
        assert turn is not None
        chosen_default = turn.options[turn.default_index].value
        assert chosen_default == "iso9001_minimalist_5state"
        # And the option must carry the "your last choice" tag
        labels = [opt.note or "" for opt in turn.options]
        assert any("last choice" in lab for lab in labels)

    def test_no_history_default_is_first_option(self, qms_project: Path, tmp_path: Path):
        empty_store = HistoryStore(path=tmp_path / "fresh.jsonl")
        session = ConsultantSession(qms_project, history=empty_store)
        session.load_project()
        # Walk to the variant question
        session.answer(session.next_turn(), 0)
        turn = session.next_turn()
        iso_idx = next(
            i for i, opt in enumerate(turn.options) if opt.value == "iso9001"
        )
        session.answer(turn, iso_idx)
        turn = session.next_turn()
        # No history: default falls back to the first variant (CeSPI 8-state)
        assert turn.options[turn.default_index].value == "cespi_unlp_8state"


# ----------------------------------------------------------------------
# Consult writes a history entry on success
# ----------------------------------------------------------------------


class TestConsultWritesHistory:
    def test_consult_appends_history_entry(
        self, qms_project: Path, tmp_path: Path, isolated_history: Path
    ):
        runner = CliRunner()
        out_dir = tmp_path / "outputs"
        result = runner.invoke(
            app,
            ["consult", str(qms_project), "--auto-accept", "--output-dir", str(out_dir)],
        )
        assert result.exit_code == 0, result.stdout
        # History file written to the isolated path
        assert isolated_history.exists()
        store = HistoryStore(path=isolated_history)
        entries = store.all_entries()
        assert len(entries) == 1
        assert entries[0].discipline_id == "quality_management"
        assert entries[0].domain_id == "iso9001"
        assert entries[0].variant_id == "cespi_unlp_8state"


# ----------------------------------------------------------------------
# CLI commands
# ----------------------------------------------------------------------


class TestHistoryCLI:
    def test_history_empty_shows_hint(self, isolated_history: Path, monkeypatch):
        # isolated_history points to a path that doesn't exist yet
        runner = CliRunner()
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
        assert "No history recorded yet" in result.stdout

    def test_history_lists_entries(
        self, qms_project: Path, tmp_path: Path, isolated_history: Path
    ):
        # Seed via a real consult run
        runner = CliRunner()
        out_dir = tmp_path / "outputs"
        runner.invoke(
            app,
            ["consult", str(qms_project), "--auto-accept", "--output-dir", str(out_dir)],
        )
        # Now list
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
        assert "calibration history" in result.stdout.lower()
        assert "iso9001" in result.stdout
        assert "cespi_unlp_8state" in result.stdout

    def test_history_clear_removes_file(
        self, qms_project: Path, tmp_path: Path, isolated_history: Path
    ):
        runner = CliRunner()
        out_dir = tmp_path / "outputs"
        runner.invoke(
            app,
            ["consult", str(qms_project), "--auto-accept", "--output-dir", str(out_dir)],
        )
        assert isolated_history.exists()
        result = runner.invoke(app, ["history", "--clear"])
        assert result.exit_code == 0
        assert "cleared" in result.stdout.lower()
        assert not isolated_history.exists()
