"""
ReverseStatePattern: Abstract base class for domain-specific reverse flow patterns.

Each domain (ISO 9001, Software, AI/ML, Tender, etc.) contributes a plugin that defines
how to safely reverse process states based on domain-specific constraints and regulations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from forgemind.schemas.project import ProjectAnalysis


@dataclass
class ReverseStep:
    """Single step in a reversal process."""
    step_number: int
    action: str
    approval_required: bool
    approval_role: Optional[str] = None
    estimated_time_minutes: Optional[int] = None
    data_loss_risk: str = "none"  # none, low, medium, high
    notes: Optional[str] = None


@dataclass
class ReverseStateDefinition:
    """
    Defines if/how a state can be reversed to prior states.

    Example:
        State "Signed" in ISO 9001:
        - can_revert_to: ["Approved"]
        - reversible: False  (regulatory constraint)
        - reason: "Signed documents are historical records"
        - mitigation: "Issue new approved version + obsolete old"
    """
    state_name: str
    can_revert_to: List[str]
    reversible: bool
    reason: Optional[str] = None
    mitigation: Optional[str] = None
    data_loss: str = "none"
    audit_entry_template: Optional[str] = None


@dataclass
class ReversalPlan:
    """Complete plan to reverse from current_state to target_state."""
    current_state: str
    target_state: str
    rollback_path: str  # e.g., "Approved → Under Review → Draft"
    steps: List[ReverseStep]
    total_estimated_time_minutes: int
    highest_data_loss_risk: str
    approval_gates: List[str]
    dependencies: List[str]
    constraints: List[str]
    confidence: float  # 0.0-1.0: how certain is this reversible?


class ReverseStatePattern(ABC):
    """
    Abstract interface for domain-specific reverse state machine patterns.

    Subclasses (ISO9001ReversePattern, SoftwareReversePattern, etc.) define:
    - What states exist in this domain
    - Which transitions are reversible
    - What approvals/gates are required
    - What regulations constrain reversals
    """

    # Must be set by subclass
    domain: str  # e.g., "iso9001", "software", "ai_ml", "tender"
    framework: str  # e.g., "ISO 9001:2015 §8.5.6"
    description: str

    @abstractmethod
    def get_supported_states(self) -> List[ReverseStateDefinition]:
        """
        Return all states this domain supports and their reversal rules.

        Returns:
            List of ReverseStateDefinition objects defining state machine
        """
        pass

    @abstractmethod
    def generate_reversal_plan(
        self,
        project: ProjectAnalysis,
        current_state: str,
        target_state: Optional[str] = None,
    ) -> ReversalPlan:
        """
        Generate a concrete reversal plan for this project.

        Args:
            project: ProjectAnalysis with context about the project
            current_state: The state we're trying to revert FROM
            target_state: Optional - the state to revert TO (defaults to previous)

        Returns:
            ReversalPlan with specific steps, time estimates, and constraints

        Raises:
            ValueError: If reversal is not possible for this domain
        """
        pass

    @abstractmethod
    def validate_state_transition(
        self, from_state: str, to_state: str
    ) -> Dict[str, Any]:
        """
        Check if a state transition is valid in this domain.

        Returns:
            {
                "is_valid": bool,
                "reason": str,
                "requires_approval": bool,
                "approval_role": str,
                "data_loss": str,
            }
        """
        pass

    def format_for_markdown(self, reversal_plan: ReversalPlan) -> str:
        """Format reversal plan as Markdown for output."""
        lines = [
            f"## Reversal Plan: {reversal_plan.current_state} → {reversal_plan.target_state}",
            f"\n**Framework:** {self.framework}",
            f"\n**Rollback Path:** `{reversal_plan.rollback_path}`",
            f"\n### Steps\n",
        ]

        for step in reversal_plan.steps:
            approval_str = ""
            if step.approval_required and step.approval_role:
                approval_str = f" (requires {step.approval_role} approval)"

            time_str = ""
            if step.estimated_time_minutes:
                time_str = f" — ~{step.estimated_time_minutes}min"

            lines.append(f"**{step.step_number}.** {step.action}{approval_str}{time_str}")

            if step.notes:
                lines.append(f"   - {step.notes}")

            if step.data_loss_risk != "none":
                lines.append(f"   - ⚠️ Data loss risk: {step.data_loss_risk}")

        lines.extend([
            f"\n### Summary",
            f"- **Total Time:** ~{reversal_plan.total_estimated_time_minutes} minutes",
            f"- **Data Loss Risk:** {reversal_plan.highest_data_loss_risk}",
            f"- **Approval Gates:** {', '.join(reversal_plan.approval_gates) or 'None'}",
        ])

        if reversal_plan.constraints:
            lines.append(f"\n### Constraints")
            for constraint in reversal_plan.constraints:
                lines.append(f"- {constraint}")

        if reversal_plan.dependencies:
            lines.append(f"\n### Dependencies")
            for dep in reversal_plan.dependencies:
                lines.append(f"- {dep}")

        return "\n".join(lines)
