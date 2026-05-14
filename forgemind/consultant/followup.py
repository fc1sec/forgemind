"""Follow-up consultant session — revisit specific decisions in depth.

After `forgemind consult` produces 17 documents, users often need to go deeper
on one specific decision: which variant did we pick and why? Which risks are
most critical? What does the escalation contact actually mean for THIS project?

A real consultant supports that follow-up explicitly. This module powers the
`forgemind followup <output_dir>` command.

The follow-up session is driven by:
  - `consultant_calibration.json`  (machine-readable sidecar written by consult)
  - The original project file       (re-parsed for fresh analysis)
  - The bundled taxonomy            (for boundary disclosure)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from forgemind.disciplines import DisciplineTaxonomy, get_taxonomy

# ----------------------------------------------------------------------
# Loaded calibration sidecar
# ----------------------------------------------------------------------


@dataclass
class LoadedCalibration:
    """The calibration record loaded from disk for a follow-up session."""

    project_file: Path
    taxonomy_version: str
    discipline: dict | None = None
    domain: dict | None = None
    variant: dict | None = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_json(cls, json_path: Path) -> LoadedCalibration:
        if not json_path.exists():
            raise FileNotFoundError(
                f"Calibration sidecar not found at {json_path}. "
                f"Was this output directory produced by `forgemind consult`?"
            )
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        return cls(
            project_file=Path(raw.get("project_file", "")),
            taxonomy_version=str(raw.get("taxonomy_version", "")),
            discipline=raw.get("discipline"),
            domain=raw.get("domain"),
            variant=raw.get("variant"),
            raw=raw,
        )


# ----------------------------------------------------------------------
# Follow-up topics — each is a self-contained explanation
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class FollowupTopic:
    """One item the user can pick from the follow-up menu."""

    key: str               # short id, e.g. "variant"
    label: str             # menu label
    description: str       # one-line hint shown next to the label


# The menu is intentionally small. Each topic resolves to a rendering method
# in FollowupSession; adding a new topic requires adding both the FollowupTopic
# entry AND the corresponding `_render_<key>` method.
DEFAULT_TOPICS: tuple[FollowupTopic, ...] = (
    FollowupTopic(
        key="variant",
        label="Review the variant choice and its boundary conditions",
        description="Why this variant was picked; what gaps it has for your context",
    ),
    FollowupTopic(
        key="risks",
        label="Walk me through the risks one by one",
        description="Re-list each risk in the generated RISK_REGISTER.md",
    ),
    FollowupTopic(
        key="acceptance",
        label="Walk me through the acceptance criteria",
        description="Re-list each acceptance criterion in ACCEPTANCE_CRITERIA.md",
    ),
    FollowupTopic(
        key="escalation",
        label="Show the escalation path for this project",
        description="Who to contact for high-stakes decisions in this domain",
    ),
)


# ----------------------------------------------------------------------
# Session
# ----------------------------------------------------------------------


class FollowupSession:
    """Drive a follow-up consultation against a previously-generated output dir.

    The session is deliberately stateless across topic selections: the user
    can dip into any topic in any order, and exiting is always an option.
    """

    def __init__(
        self,
        output_dir: Path,
        taxonomy: DisciplineTaxonomy | None = None,
        topics: tuple[FollowupTopic, ...] = DEFAULT_TOPICS,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.taxonomy = taxonomy or get_taxonomy()
        self.topics = topics
        self.calibration: LoadedCalibration | None = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Locate and parse the calibration sidecar."""
        json_path = self.output_dir / "consultant_calibration.json"
        self.calibration = LoadedCalibration.from_json(json_path)

    # ------------------------------------------------------------------
    # Menu rendering + topic resolution
    # ------------------------------------------------------------------

    def menu_lines(self) -> list[str]:
        """Render the topic menu (numbered)."""
        lines = ["Follow-up — what would you like to revisit?"]
        for i, topic in enumerate(self.topics, start=1):
            lines.append(f"  {i}) {topic.label}")
            lines.append(f"     [dim]{topic.description}[/dim]")
        lines.append(f"  {len(self.topics) + 1}) Done")
        return lines

    def is_done_choice(self, choice_index: int) -> bool:
        """Return True if the choice index corresponds to the 'Done' entry."""
        return choice_index == len(self.topics)

    def topic_for_choice(self, choice_index: int) -> FollowupTopic | None:
        """Resolve a 0-based menu index to a FollowupTopic, or None for Done."""
        if 0 <= choice_index < len(self.topics):
            return self.topics[choice_index]
        return None

    # ------------------------------------------------------------------
    # Topic renderers — pure functions returning the lines to print.
    # Kept separate so they can be exercised in tests without mocking I/O.
    # ------------------------------------------------------------------

    def render_topic(self, topic_key: str) -> list[str]:
        """Render the body for a topic key. Returns lines (no trailing newlines)."""
        if self.calibration is None:
            raise RuntimeError("Call load() before render_topic()")
        method = getattr(self, f"_render_{topic_key}", None)
        if method is None:
            return [f"(No renderer for topic '{topic_key}')"]
        return method()

    # ----- variant -----
    def _render_variant(self) -> list[str]:
        c = self.calibration
        assert c is not None
        v = c.variant
        lines = ["## Variant choice review"]
        if not v:
            lines.append("No variant was selected at calibration time.")
            return lines
        lines.append(f"- Variant: {v['name']} (`{v['id']}`)")
        if v.get("source"):
            lines.append(f"- Source: {v['source']}")
        if v.get("url"):
            lines.append(f"- URL: {v['url']}")
        if v.get("confidence") is not None:
            lines.append(f"- Confidence: {v['confidence']:.0%}")
        if v.get("production_validated"):
            lines.append("- Production-validated: yes")
        if v.get("when_to_choose"):
            lines.append("- Reasons this variant fit your context:")
            for r in v["when_to_choose"]:
                lines.append(f"  - {r}")
        if v.get("pros"):
            lines.append("- Pros:")
            for p in v["pros"]:
                lines.append(f"  - {p}")
        if v.get("cons"):
            lines.append("- Cons (residual gaps to watch):")
            for c_ in v["cons"]:
                lines.append(f"  - {c_}")
        d = c.domain or {}
        bc = d.get("boundary_conditions") or []
        if bc:
            lines.append("- Domain-level boundary conditions:")
            for b in bc:
                lines.append(f"  - {b}")
        return lines

    # ----- risks -----
    def _render_risks(self) -> list[str]:
        risks_md = self.output_dir / "RISK_REGISTER.md"
        if not risks_md.exists():
            return [f"RISK_REGISTER.md not found at {risks_md}"]
        return [
            "## Risks (from RISK_REGISTER.md)",
            "",
            risks_md.read_text(encoding="utf-8").strip(),
        ]

    # ----- acceptance -----
    def _render_acceptance(self) -> list[str]:
        acc_md = self.output_dir / "ACCEPTANCE_CRITERIA.md"
        if not acc_md.exists():
            return [f"ACCEPTANCE_CRITERIA.md not found at {acc_md}"]
        return [
            "## Acceptance criteria (from ACCEPTANCE_CRITERIA.md)",
            "",
            acc_md.read_text(encoding="utf-8").strip(),
        ]

    # ----- escalation -----
    def _render_escalation(self) -> list[str]:
        c = self.calibration
        assert c is not None
        d = c.domain or {}
        lines = ["## Escalation path"]
        if d.get("escalate_to"):
            lines.append(f"- Domain-level contact: {d['escalate_to']}")
        else:
            lines.append("- No domain-level escalation contact recorded.")
        # Taxonomy-level boundary disclosures provide the WHY behind escalation
        bc = d.get("boundary_conditions") or []
        if bc:
            lines.append("- Reasons to escalate:")
            for b in bc:
                lines.append(f"  - {b}")
        lines.append("")
        lines.append(
            "Always escalate for high-stakes decisions: ForgeMind outputs are "
            "STOCHASTIC and require expert validation before commitment."
        )
        return lines
