"""Calibration session for the ForgeMind consultant.

The session is an explicit state machine so it can be driven both from an
interactive CLI and from automated tests / CI runs.

Lifecycle:
    1. classify        — read project, score candidate disciplines
    2. ask_discipline  — disambiguate among plausible disciplines
    3. ask_domain      — pick a domain within the chosen discipline
    4. ask_variant     — pick a variant (skipped if only one)
    5. disclose        — show coverage status + boundary conditions
    6. confirm         — confirm proceed (or cancel)

Each step that produces a question yields a ConsultantTurn. The caller
(CLI or test) feeds back an answer via `answer(...)`. Questions are skipped
automatically when there is no ambiguity.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from forgemind.core.classifier import classify_domain
from forgemind.core.intake import parse_markdown
from forgemind.disciplines import Coverage, Discipline, Domain, get_taxonomy
from forgemind.disciplines.taxonomy import DisciplineTaxonomy, Variant

# ----------------------------------------------------------------------
# Mapping from the keyword-classifier output → taxonomy discipline ids
# ----------------------------------------------------------------------

CLASSIFIER_TO_DISCIPLINE: dict[str, str] = {
    "ai_project": "ai_ml",
    "software_project": "software_engineering",
    "qms_iso": "quality_management",
    "operations": "operations_methodops",
    "odoo_erp": "operations_methodops",
    "tenders": "OUT_OF_SCOPE",  # tender / procurement = regulated; refuse
}

# When the classifier emits one of these, we map it to an out-of-scope-by-design
# entry in the taxonomy (or to a generic refusal if none matches).
CLASSIFIER_TO_OUT_OF_SCOPE: dict[str, str] = {
    "tenders": "legal_advice",
}


# ----------------------------------------------------------------------
# Public dataclasses
# ----------------------------------------------------------------------


class CalibrationOutcome(str, Enum):
    """Final outcome of a calibration session."""

    READY = "ready"               # user confirmed; proceed with generation
    CANCELLED = "cancelled"        # user opted out
    REFUSED = "refused"            # ForgeMind refuses (out of scope / not covered)


@dataclass(frozen=True)
class ConsultantOption:
    """One option in a consultant question."""

    label: str          # short label the user sees
    value: str          # internal value the option resolves to
    note: str | None = None       # parenthetical detail (e.g. "[PARTIAL]")
    will_escalate: bool = False      # picking this option triggers refusal


@dataclass(frozen=True)
class ConsultantTurn:
    """A single Q&A in the calibration dialog."""

    step: int
    total_steps: int
    purpose: str            # short label of what is being calibrated
    question: str
    options: tuple[ConsultantOption, ...]
    default_index: int | None = None  # 0-based default option

    def render_options(self) -> list[str]:
        """Return printable strings for each option."""
        rendered = []
        for i, opt in enumerate(self.options, start=1):
            line = f"  {i}) {opt.label}"
            if opt.note:
                line += f"  {opt.note}"
            rendered.append(line)
        return rendered


# ----------------------------------------------------------------------
# Session
# ----------------------------------------------------------------------


@dataclass
class _Calibration:
    """Internal calibration state — what the user has chosen so far."""

    discipline: Discipline | None = None
    domain: Domain | None = None
    variant: Variant | None = None
    discipline_candidates: tuple[Discipline, ...] = ()
    refusal_reason: str | None = None
    cancelled: bool = False
    confirmed: bool = False  # True once user answered the confirmation question
    # Sentinel: user explicitly chose "generic" at the domain step so we should
    # NOT keep asking the domain question. Without this, a None `domain` means
    # "not yet answered" AND "answered generic" — ambiguous.
    domain_answered: bool = False
    # Set True for one turn when the user picks "compare variants first" so
    # the CLI knows to render the comparison view; cleared on the next answer.
    comparison_requested: bool = False


class ConsultantSession:
    """Drives the calibration dialog for a single project file."""

    MAX_STEPS = 4

    def __init__(
        self,
        project_file: Path,
        taxonomy: DisciplineTaxonomy | None = None,
    ) -> None:
        self.project_file = Path(project_file)
        self.taxonomy = taxonomy or get_taxonomy()
        self._calibration = _Calibration()
        self._project_input = None
        self._classifier_output: str | None = None

    # ------------------------------------------------------------------
    # Public read-only accessors
    # ------------------------------------------------------------------

    @property
    def calibration(self) -> _Calibration:
        return self._calibration

    @property
    def project_input(self):
        return self._project_input

    @property
    def classifier_output(self) -> str | None:
        return self._classifier_output

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load_project(self) -> None:
        """Parse the project file and run the keyword classifier."""
        if not self.project_file.exists():
            raise FileNotFoundError(f"Project file not found: {self.project_file}")
        self._project_input = parse_markdown(str(self.project_file))
        domain_id, _detected = classify_domain(self._project_input)
        self._classifier_output = domain_id

        # If the classifier maps to an out-of-scope-by-design entry, refuse
        # immediately — calibration cannot rescue this.
        if CLASSIFIER_TO_DISCIPLINE.get(domain_id) == "OUT_OF_SCOPE":
            entry_id = CLASSIFIER_TO_OUT_OF_SCOPE.get(domain_id, "")
            entry = self.taxonomy.out_of_scope.get(entry_id)
            if entry:
                self._calibration.refusal_reason = (
                    f"Detected '{domain_id}' which falls under '{entry.id}': "
                    f"{entry.reason} Escalate to: {entry.escalate_to}."
                )
            else:
                self._calibration.refusal_reason = (
                    f"Detected '{domain_id}' which is out of scope by design."
                )
            return

        # Build the discipline candidates list, preferring the classifier hit.
        candidates: list[Discipline] = []
        primary_id = CLASSIFIER_TO_DISCIPLINE.get(domain_id)
        if primary_id:
            primary = self.taxonomy.get_discipline(primary_id)
            if primary:
                candidates.append(primary)
        # Always include quality_management + software_engineering as runners-up
        # for "generic" projects so the user can disambiguate.
        for fallback_id in ("quality_management", "software_engineering", "operations_methodops"):
            if fallback_id == primary_id:
                continue
            d = self.taxonomy.get_discipline(fallback_id)
            if d and d not in candidates:
                candidates.append(d)
        self._calibration.discipline_candidates = tuple(candidates)

    # ------------------------------------------------------------------
    # Question builders — each returns None when no calibration is needed
    # ------------------------------------------------------------------

    def next_turn(self) -> ConsultantTurn | None:
        """Return the next ConsultantTurn that requires user input, or None."""
        c = self._calibration
        if c.refusal_reason or c.cancelled or c.confirmed:
            return None

        if c.discipline is None:
            return self._build_discipline_question()
        if not c.domain_answered:
            return self._build_domain_question()
        if c.variant is None and self._needs_variant_question():
            return self._build_variant_question()
        return self._build_confirm_question()

    def _build_discipline_question(self) -> ConsultantTurn:
        candidates = self._calibration.discipline_candidates
        # Detect classifier output for the note
        note_for = self._classifier_output
        options = []
        for i, disc in enumerate(candidates):
            note = (
                f"  [detected: {note_for}]" if i == 0 and note_for else None
            )
            options.append(
                ConsultantOption(label=disc.name, value=disc.id, note=note)
            )
        options.append(
            ConsultantOption(
                label="None of the above / I'll specify another discipline",
                value="__other__",
            )
        )
        return ConsultantTurn(
            step=1,
            total_steps=self.MAX_STEPS,
            purpose="Discipline calibration",
            question="Which discipline best describes this project?",
            options=tuple(options),
            default_index=0,
        )

    def _build_domain_question(self) -> ConsultantTurn:
        assert self._calibration.discipline is not None
        disc = self._calibration.discipline
        options: list[ConsultantOption] = []
        for domain in disc.domains.values():
            note = self._coverage_note(domain)
            options.append(
                ConsultantOption(
                    label=domain.name,
                    value=domain.id,
                    note=note,
                    will_escalate=(domain.coverage == Coverage.NOT_COVERED),
                )
            )
        options.append(
            ConsultantOption(
                label="None of the above / generic project planning",
                value="__generic__",
            )
        )
        return ConsultantTurn(
            step=2,
            total_steps=self.MAX_STEPS,
            purpose=f"Domain within {disc.name}",
            question="Which specific domain applies?",
            options=tuple(options),
            default_index=0,
        )

    def _needs_variant_question(self) -> bool:
        """Variant question is only shown if the domain has 2+ variants."""
        d = self._calibration.domain
        return d is not None and len(d.variants) >= 2

    def _build_variant_question(self) -> ConsultantTurn:
        assert self._calibration.domain is not None
        variant_options = [
            ConsultantOption(
                label=v.name,
                value=v.id,
                note=f"  [confidence {v.confidence:.0%}{', production' if v.production_validated else ''}]",
            )
            for v in self._calibration.domain.variants
        ]
        # Add the "compare side-by-side first" option ONLY if at least one
        # variant has documented decision criteria; otherwise the comparison
        # view is empty and the option is useless.
        any_criteria = any(
            v.when_to_choose or v.pros or v.cons
            for v in self._calibration.domain.variants
        )
        if any_criteria:
            variant_options.append(
                ConsultantOption(
                    label="Show me a side-by-side comparison first",
                    value="__compare__",
                    note="  [no choice made yet]",
                )
            )
        return ConsultantTurn(
            step=3,
            total_steps=self.MAX_STEPS,
            purpose=f"Variant within {self._calibration.domain.name}",
            question="Which validated variant best matches your context?",
            options=tuple(variant_options),
            default_index=0,
        )

    def render_variant_comparison(self) -> list[str]:
        """Return human-readable side-by-side comparison lines for the
        current domain's variants. Called by the CLI when the user picks
        '__compare__' at the variant step.
        """
        d = self._calibration.domain
        if d is None or not d.variants:
            return ["No variants to compare."]
        lines: list[str] = [f"Variant comparison for {d.name}:"]
        for v in d.variants:
            lines.append("")
            lines.append(f"=== {v.name} ({v.id}) ===")
            prod = " · production-validated" if v.production_validated else ""
            lines.append(f"Confidence: {v.confidence:.0%}{prod}")
            if v.source:
                lines.append(f"Source: {v.source}")
            if v.when_to_choose:
                lines.append("Choose this if:")
                for criterion in v.when_to_choose:
                    lines.append(f"  • {criterion}")
            if v.pros:
                lines.append("Pros:")
                for p in v.pros:
                    lines.append(f"  + {p}")
            if v.cons:
                lines.append("Cons:")
                for c in v.cons:
                    lines.append(f"  - {c}")
        return lines

    def _build_confirm_question(self) -> ConsultantTurn:
        d = self._calibration.domain
        confirm_options = (
            ConsultantOption(label="Yes, generate outputs with these caveats", value="yes"),
            ConsultantOption(label="No, cancel and don't generate", value="no"),
        )
        # Compose a short summary for the question text
        if d is None:
            summary = "Generic planning (no specific domain selected)"
        else:
            summary = (
                f"{d.name} — coverage {d.coverage.value}"
                + (f", confidence {d.confidence:.0%}" if d.confidence is not None else "")
            )
        return ConsultantTurn(
            step=4,
            total_steps=self.MAX_STEPS,
            purpose="Proceed confirmation",
            question=f"Proceed with: {summary}?",
            options=confirm_options,
            default_index=0,
        )

    # ------------------------------------------------------------------
    # Answer handling
    # ------------------------------------------------------------------

    def answer(self, turn: ConsultantTurn, choice_index: int) -> None:
        """Apply an answer (0-based index) to a turn."""
        if not 0 <= choice_index < len(turn.options):
            raise ValueError(
                f"Invalid choice {choice_index}: must be 0..{len(turn.options) - 1}"
            )
        choice = turn.options[choice_index]

        if turn.purpose == "Discipline calibration":
            if choice.value == "__other__":
                self._calibration.refusal_reason = (
                    "You indicated the project doesn't fit any of ForgeMind's "
                    "current disciplines. Run `forgemind capabilities` to see "
                    "what's supported, or contribute a pattern."
                )
                return
            disc = self.taxonomy.get_discipline(choice.value)
            if disc is None:
                self._calibration.refusal_reason = f"Unknown discipline: {choice.value}"
                return
            self._calibration.discipline = disc

        elif turn.purpose.startswith("Domain"):
            self._calibration.domain_answered = True
            if choice.value == "__generic__":
                # Generic mode: no specific domain, skip variant question.
                self._calibration.domain = None
                self._calibration.variant = None
                return
            domain = self.taxonomy.get_domain(choice.value)
            if domain is None:
                self._calibration.refusal_reason = f"Unknown domain: {choice.value}"
                return
            if domain.coverage == Coverage.NOT_COVERED:
                self._calibration.refusal_reason = (
                    f"'{domain.name}' is not covered by ForgeMind. "
                    f"Reason: {domain.reason or 'no patterns available'}. "
                    f"Escalate to: {domain.escalate_to or 'domain expert'}."
                )
                return
            self._calibration.domain = domain
            # If domain has exactly one variant, auto-select it (skip variant Q)
            if len(domain.variants) == 1:
                self._calibration.variant = domain.variants[0]

        elif turn.purpose.startswith("Variant"):
            assert self._calibration.domain is not None
            # Special sentinel: user asked for comparison. Stay on the variant
            # step (do NOT set variant) and signal the caller to render the
            # comparison view, then re-ask the question.
            if choice.value == "__compare__":
                self._calibration.comparison_requested = True
                return
            self._calibration.comparison_requested = False
            for v in self._calibration.domain.variants:
                if v.id == choice.value:
                    self._calibration.variant = v
                    return
            self._calibration.refusal_reason = f"Unknown variant: {choice.value}"

        elif turn.purpose == "Proceed confirmation":
            if choice.value == "no":
                self._calibration.cancelled = True
            else:
                self._calibration.confirmed = True

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    def outcome(self) -> CalibrationOutcome:
        c = self._calibration
        if c.refusal_reason:
            return CalibrationOutcome.REFUSED
        if c.cancelled:
            return CalibrationOutcome.CANCELLED
        # READY requires explicit user confirmation at the confirm step.
        # Anything short of that is treated as "still in progress" which we
        # surface as CANCELLED so callers don't proceed with generation.
        if c.confirmed:
            return CalibrationOutcome.READY
        return CalibrationOutcome.CANCELLED

    def disclosures(self) -> list[str]:
        """Return human-readable disclosures (boundaries, refusal, etc.)."""
        c = self._calibration
        lines: list[str] = []
        if c.refusal_reason:
            lines.append(f"REFUSED: {c.refusal_reason}")
            return lines
        if c.discipline:
            lines.append(f"Discipline: {c.discipline.name}")
        if c.domain:
            cov = c.domain.coverage.value
            lines.append(f"Domain: {c.domain.name} (coverage: {cov})")
            if c.domain.confidence is not None:
                lines.append(f"Confidence: {c.domain.confidence:.0%}")
            for bc in c.domain.boundary_conditions:
                lines.append(f"  - Known gap: {bc}")
            if c.domain.escalate_to:
                lines.append(f"Escalate to (for high-stakes decisions): {c.domain.escalate_to}")
        if c.variant:
            lines.append(f"Selected variant: {c.variant.name} ({c.variant.id})")
            if c.variant.source:
                lines.append(f"  Source: {c.variant.source}")
        if not c.domain and c.discipline:
            lines.append(
                "Generic mode: ForgeMind will use cross-discipline templates only. "
                "Outputs will be STOCHASTIC and require expert review."
            )
        return lines

    def _coverage_note(self, domain: Domain) -> str:
        if domain.coverage == Coverage.COVERED:
            return "  [COVERED]"
        if domain.coverage == Coverage.PARTIAL:
            conf = (
                f", {domain.confidence:.0%}" if domain.confidence is not None else ""
            )
            return f"  [PARTIAL{conf}]"
        return "  [NOT COVERED — will escalate]"
