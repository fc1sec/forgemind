"""
ForgeMind Epistemic Framework v1.2.0

Prevents hallucination by validating that outputs stay within:
- DETERMINISTIC bounds (facts from standards/project data)
- STOCHASTIC bounds (empirical patterns with confidence margins)
- Rejects SPECULATIVE outputs (invention)
"""

from .epistemic_validator import (
    EpistemicValidator,
    OutputClassification,
    ValidationResult,
)

__all__ = ["EpistemicValidator", "OutputClassification", "ValidationResult"]
