"""
Epistemic Validator: Prevents hallucination by validating outputs stay within bounds.

Three language types:
1. DETERMINISTIC: Facts from official standards or project analysis
2. STOCHASTIC: Empirical patterns with explicit confidence margins
3. SPECULATIVE: Invention without expertise — REJECTED
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OutputClassification(Enum):
    """Classification of output type and certainty."""
    DETERMINISTIC = "fact_based"  # From standards/project data
    STOCHASTIC = "empirical"  # From knowledge graph (labeled with confidence)
    SPECULATIVE = "uncertain"  # Invention — REJECTED
    ESCALATE = "out_of_scope"  # Domain not yet supported


@dataclass
class ValidationResult:
    """Result of epistemic validation."""
    is_valid: bool
    classification: OutputClassification
    confidence: float  # 0.0-1.0
    language_type: str  # "deterministic" | "stochastic" | "speculative"
    sources: list[str]  # What grounds this output?
    message: str  # Why valid/invalid?
    escalation_needed: bool = False
    escalate_to: Optional[str] = None  # "iso_expert", "qms_consultant", etc.
    requires_label: bool = False  # Should output have confidence label?
    suggested_label: str = ""  # What label to add?


class EpistemicValidator:
    """
    Validates that ForgeMind outputs stay within epistemic bounds.

    Usage:
        validator = EpistemicValidator(registry=plugin_registry)
        result = validator.validate_output(
            output_text=recommendation,
            confidence=0.65,
            domain="iso9001",
            sources=["knowledge_graph"]
        )

        if not result.is_valid:
            escalate_to_expert(result.escalate_to)
        elif result.requires_label:
            add_confidence_marker(result.suggested_label)
    """

    # Confidence thresholds
    CONFIDENCE_THRESHOLD_DETERMINISTIC = 0.90
    CONFIDENCE_THRESHOLD_STOCHASTIC = 0.60
    CONFIDENCE_THRESHOLD_ESCALATE = 0.50

    # Speculative language patterns (detector)
    SPECULATIVE_PHRASES = {
        "probably should": "speculative recommendation",
        "we think you should": "speculative advice",
        "in our experience": "ungrounded experience claim",
        "most teams do": "unvalidated generalization",
        "we recommend": "advice without source",
        "you should consider": "unsourced suggestion",
        "best practice would be": "best practice without reference",
        "typically": "unvalidated generalization",
        "generally": "unvalidated generalization",
        "usually": "unvalidated generalization",
        "in most cases": "unvalidated generalization",
        "the way to": "instruction without basis",
        "the best approach": "unsourced guidance",
    }

    # Source confidence weights
    SOURCE_CONFIDENCE = {
        "official_standard": 0.95,  # ISO 9001, IEEE, NIST, etc.
        "expert_plugin": 0.85,  # Expert-contributed reverse pattern
        "knowledge_graph_high_n": 0.70,  # 50+ similar projects
        "knowledge_graph_medium_n": 0.60,  # 20-50 projects
        "knowledge_graph_low_n": 0.45,  # <20 projects
        "project_analysis": 0.80,  # Facts from user's project
        "regulatory_documentation": 0.95,
        "industry_best_practice": 0.70,  # With citation
    }

    def __init__(self, plugin_registry=None, taxonomy=None):
        """
        Initialize validator.

        Args:
            plugin_registry: Optional PluginRegistry to check domain expertise
            taxonomy: Optional DisciplineTaxonomy. If omitted, the bundled
                disciplines.yaml is loaded lazily on first use. Passing one
                explicitly is useful in tests to control coverage claims.
        """
        self.plugin_registry = plugin_registry
        self._taxonomy = taxonomy

        # Legacy hardcoded fallbacks — preserved so the validator still works
        # if the taxonomy YAML is unavailable. The taxonomy, when loaded,
        # supersedes these.
        self.known_unknowns: set[str] = {
            "hardware_firmware",
            "government_tender",
            "biomedical_device",
            "nuclear_systems",
        }
        self.partial_domains: dict[str, str] = {
            "ai_ml": "checkpoint restore + feature flags only",
            "software": "git + blue-green, missing: service mesh",
        }

    @property
    def taxonomy(self):
        """Lazily load and cache the discipline taxonomy."""
        if self._taxonomy is None:
            try:
                from forgemind.disciplines import get_taxonomy

                self._taxonomy = get_taxonomy()
            except (FileNotFoundError, ValueError, ImportError):
                # Fall back to hardcoded sets if YAML missing/malformed
                self._taxonomy = None
        return self._taxonomy

    def validate_output(
        self,
        output_text: str,
        confidence: float,
        domain: str,
        sources: list[str],
    ) -> ValidationResult:
        """
        Validate that output doesn't hallucinate beyond available expertise.

        Args:
            output_text: The generated output to validate
            confidence: Confidence 0.0-1.0 from the generator
            domain: Project domain ("iso9001", "software", etc.)
            sources: What grounds this output? (e.g., ["standard", "knowledge_graph"])

        Returns:
            ValidationResult with validity + required actions
        """

        # Layer 1: Detect speculation
        speculation_score = self._detect_speculation(output_text)
        if speculation_score > 0.5:  # Likely speculative
            if not self._has_sources(sources):
                return ValidationResult(
                    is_valid=False,
                    classification=OutputClassification.SPECULATIVE,
                    confidence=0.0,
                    language_type="speculative",
                    sources=sources,
                    message="Output contains speculative language without grounding sources",
                    escalation_needed=True,
                    escalate_to=self._get_escalation_contact(domain),
                )

        # Layer 2: Check domain expertise exists
        if self._is_unsupported_domain(domain):
            return ValidationResult(
                is_valid=False,
                classification=OutputClassification.ESCALATE,
                confidence=0.0,
                language_type="out_of_scope",
                sources=sources,
                message=f"Domain '{domain}' not yet in ForgeMind plugin ecosystem",
                escalation_needed=True,
                escalate_to=self._get_escalation_contact(domain),
            )

        # Layer 3: Check confidence against classification
        sources_confidence = self._score_sources(sources)
        if sources_confidence is None:
            # No valid sources
            return ValidationResult(
                is_valid=False,
                classification=OutputClassification.SPECULATIVE,
                confidence=0.0,
                language_type="speculative",
                sources=sources,
                message="Output not grounded in sources (standards, knowledge graph, or expertise)",
                escalation_needed=True,
                escalate_to=self._get_escalation_contact(domain),
            )

        # Layer 4: Determine classification and whether to label
        if sources_confidence >= self.CONFIDENCE_THRESHOLD_DETERMINISTIC:
            # Deterministic: facts from standards/project data
            return ValidationResult(
                is_valid=True,
                classification=OutputClassification.DETERMINISTIC,
                confidence=sources_confidence,
                language_type="deterministic",
                sources=sources,
                message="Output grounded in standards or project facts",
                requires_label=False,
            )

        elif sources_confidence >= self.CONFIDENCE_THRESHOLD_STOCHASTIC:
            # Stochastic: empirical pattern, label with confidence
            return ValidationResult(
                is_valid=True,
                classification=OutputClassification.STOCHASTIC,
                confidence=sources_confidence,
                language_type="stochastic",
                sources=sources,
                message="Output based on empirical patterns — must be labeled with confidence",
                requires_label=True,
                suggested_label=self._format_confidence_label(sources_confidence, sources),
            )

        else:
            # Below threshold: escalate
            return ValidationResult(
                is_valid=False,
                classification=OutputClassification.STOCHASTIC,
                confidence=sources_confidence,
                language_type="stochastic",
                sources=sources,
                message=f"Confidence {sources_confidence:.0%} below {self.CONFIDENCE_THRESHOLD_STOCHASTIC:.0%} threshold — requires expert review",
                escalation_needed=True,
                escalate_to=self._get_escalation_contact(domain),
            )

    # Private helper methods

    def _detect_speculation(self, text: str) -> float:
        """
        Detect speculative language patterns.

        Returns:
            Score 0.0-1.0 indicating likelihood of speculation
        """
        text_lower = text.lower()
        matches = 0
        for phrase in self.SPECULATIVE_PHRASES:
            if phrase in text_lower:
                matches += 1

        return min(1.0, matches / 5.0)  # Normalize to 0-1

    def _has_sources(self, sources: list[str]) -> bool:
        """Check if output has any valid sources."""
        return len(sources) > 0 and any(s in self.SOURCE_CONFIDENCE for s in sources)

    def _score_sources(self, sources: list[str]) -> Optional[float]:
        """
        Score confidence based on source types.

        Returns:
            Average confidence from sources, or None if no valid sources
        """
        if not self._has_sources(sources):
            return None

        valid_sources = [s for s in sources if s in self.SOURCE_CONFIDENCE]
        if not valid_sources:
            return None

        scores = [self.SOURCE_CONFIDENCE[s] for s in valid_sources]
        return sum(scores) / len(scores)

    def _is_unsupported_domain(self, domain: str) -> bool:
        """Check if domain is completely unsupported.

        Consults the discipline taxonomy when available; falls back to the
        hardcoded set otherwise.
        """
        if self.taxonomy is not None:
            return self.taxonomy.must_escalate(domain)
        return domain in self.known_unknowns

    def _is_partial_domain(self, domain: str) -> bool:
        """Check if domain is partially supported.

        Consults the discipline taxonomy when available; falls back to the
        hardcoded set otherwise.
        """
        if self.taxonomy is not None:
            from forgemind.disciplines import Coverage

            return self.taxonomy.coverage_for(domain) == Coverage.PARTIAL
        return domain in self.partial_domains

    def _get_escalation_contact(self, domain: str) -> str:
        """Get who to escalate to for this domain.

        Consults the discipline taxonomy when available; falls back to the
        legacy contact map otherwise.
        """
        if self.taxonomy is not None:
            return self.taxonomy.escalation_contact(domain)

        contacts = {
            "iso9001": "QMS expert / ISO auditor",
            "software": "DevOps / SRE engineer",
            "ai_ml": "ML Ops / ML Engineer",
            "tender": "Government contracts specialist",
            "hardware_firmware": "Embedded systems engineer",
            "biomedical_device": "Biomedical engineer / FDA specialist",
        }
        return contacts.get(domain, "Domain expert")

    def _format_confidence_label(self, confidence: float, sources: list[str]) -> str:
        """Format a confidence label for stochastic output."""
        label = "\n\n**Classification:** STOCHASTIC (Empirical)\n"
        label += f"**Confidence:** {confidence:.0%}\n"
        label += f"**Sources:** {', '.join(sources)}\n"
        label += "**Note:** This is based on patterns, not certainty. Verify with domain expert."
        return label
