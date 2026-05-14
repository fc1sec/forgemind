"""
ISO 9001:2015 Reverse State Pattern

Reference implementation for QMS (Quality Management System) document reversals.

Based on ISO 9001:2015 §8.5.6 (Control of changes):
"Changes to requirements shall be reviewed and approved before implementation."

Document lifecycle in typical ISO 9001 implementations:
Draft → Under Review → Approved → Signed → [Obsolete if changed]
"""

from typing import Any, Optional

from forgemind.schemas.project import ProjectAnalysis

from .reverse_state_pattern import (
    ReversalPlan,
    ReverseStateDefinition,
    ReverseStatePattern,
    ReverseStep,
)


class ISO9001ReversePattern(ReverseStatePattern):
    """ISO 9001:2015 QMS document reversal patterns."""

    domain = "iso9001"
    framework = "ISO 9001:2015 §8.5.6 (Control of changes)"
    description = (
        "Document lifecycle reversals with audit trail for quality management systems. "
        "Defines how to safely revert document approval states while maintaining "
        "regulatory compliance and historical records."
    )

    # State machine definition
    STATE_MACHINE = {
        "Draft": {
            "can_revert_to": [],
            "reversible": True,
            "data_loss": "none",
            "reason": "Initial state, no reversions needed",
            "audit_entry": None,
        },
        "Under Review": {
            "can_revert_to": ["Draft"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Returnable to author for revisions",
            "approval_role": "document_author",
            "audit_entry": "Returned to Draft by {actor} on {timestamp}\nReason: {reason}",
        },
        "Approved": {
            "can_revert_to": ["Under Review"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Can revert to review if quality issues found",
            "approval_role": "quality_manager",
            "audit_entry": "Reverted from Approved to Under Review\nApprover: {actor}\nDate: {timestamp}\nReason: {reason}",
            "mitigation": "May trigger re-review cycle and stakeholder notification",
        },
        "Signed": {
            "can_revert_to": ["Approved"],
            "reversible": False,
            "data_loss": "none",
            "reason": "Signed documents are historical records per §4.4.2. Cannot be unsigned.",
            "mitigation": "Issue new approved version + mark old version Obsolete with change notice",
            "audit_entry": "Signed document cannot be reverted",
        },
        "Obsolete": {
            "can_revert_to": [],
            "reversible": False,
            "data_loss": "none",
            "reason": "Obsolete documents are archived per §4.4.2",
            "mitigation": "Reissue with new revision number instead",
            "audit_entry": None,
        },
    }

    def get_supported_states(self) -> list[ReverseStateDefinition]:
        """Return all states in ISO 9001 document lifecycle."""
        definitions = []
        for state_name, config in self.STATE_MACHINE.items():
            definitions.append(
                ReverseStateDefinition(
                    state_name=state_name,
                    can_revert_to=config["can_revert_to"],
                    reversible=config["reversible"],
                    reason=config.get("reason"),
                    mitigation=config.get("mitigation"),
                    data_loss=config.get("data_loss", "none"),
                    audit_entry_template=config.get("audit_entry"),
                )
            )
        return definitions

    def validate_state_transition(self, from_state: str, to_state: str) -> dict[str, Any]:
        """Check if a state transition is valid per ISO 9001."""
        if from_state not in self.STATE_MACHINE:
            return {"is_valid": False, "reason": f"Unknown source state: {from_state}"}

        if to_state not in self.STATE_MACHINE:
            return {"is_valid": False, "reason": f"Unknown target state: {to_state}"}

        config = self.STATE_MACHINE[from_state]

        if to_state not in config["can_revert_to"]:
            return {
                "is_valid": False,
                "reason": f"Cannot revert {from_state} to {to_state}",
                "constraint": config.get("reason", "No reversions defined"),
            }

        if not config["reversible"]:
            return {
                "is_valid": False,
                "reason": config.get("reason", "Reversal not permitted"),
                "mitigation": config.get("mitigation"),
            }

        return {
            "is_valid": True,
            "requires_approval": to_state == "Under Review",
            "approval_role": config.get("approval_role"),
            "data_loss": config.get("data_loss", "none"),
        }

    def generate_reversal_plan(
        self,
        project: ProjectAnalysis,
        current_state: str,
        target_state: Optional[str] = None,
    ) -> ReversalPlan:
        """Generate concrete reversal plan for this ISO project."""

        # Validate current state
        if current_state not in self.STATE_MACHINE:
            raise ValueError(f"Unknown state: {current_state}")

        # Determine target (defaults to previous in sequence)
        if target_state is None:
            possible_targets = self.STATE_MACHINE[current_state]["can_revert_to"]
            if not possible_targets:
                raise ValueError(
                    f"Cannot revert from {current_state}: {self.STATE_MACHINE[current_state]['reason']}"
                )
            target_state = possible_targets[0]

        # Validate transition
        validation = self.validate_state_transition(current_state, target_state)
        if not validation["is_valid"]:
            raise ValueError(validation["reason"])

        # Generate steps based on state pair
        if current_state == "Under Review" and target_state == "Draft":
            steps = self._steps_under_review_to_draft(project)
        elif current_state == "Approved" and target_state == "Under Review":
            steps = self._steps_approved_to_under_review(project)
        elif current_state == "Signed" and target_state == "Approved":
            steps = self._steps_signed_to_approved(project)
        else:
            steps = []

        # Calculate totals
        total_time = sum(s.estimated_time_minutes or 0 for s in steps)
        risks = [s.data_loss_risk for s in steps if s.data_loss_risk != "none"]
        highest_risk = max(risks) if risks else "none"

        approval_gates = [s.approval_role for s in steps if s.approval_required]

        return ReversalPlan(
            current_state=current_state,
            target_state=target_state,
            rollback_path=self._build_rollback_path(current_state, target_state),
            steps=steps,
            total_estimated_time_minutes=total_time,
            highest_data_loss_risk=highest_risk,
            approval_gates=list(set(approval_gates)) if approval_gates else [],
            dependencies=self._get_dependencies(current_state),
            constraints=self._get_constraints(current_state),
            confidence=0.95,  # High confidence for ISO-documented pattern
        )

    # Internal helper methods

    def _steps_under_review_to_draft(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Steps to revert from 'Under Review' back to 'Draft'."""
        return [
            ReverseStep(
                step_number=1,
                action="Author identifies reason for reversal",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=2,
                action="Update document metadata: Set status to Draft, clear review dates",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Make required edits to document",
                approval_required=False,
                estimated_time_minutes=20,
                notes="Time varies by change scope",
            ),
            ReverseStep(
                step_number=4,
                action="Add entry to change log: Reason for revision",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=5,
                action="Log reversal in audit trail per §8.5.2",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_approved_to_under_review(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Steps to revert from 'Approved' back to 'Under Review'."""
        return [
            ReverseStep(
                step_number=1,
                action="Quality manager approves reversal (compliance issue or error found)",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=15,
                notes="Use change request process per §8.5.6",
            ),
            ReverseStep(
                step_number=2,
                action="Notify document author and stakeholders of reversal",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=3,
                action="Update document status to 'Under Review'",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=4,
                action="Make required changes (compliance fixes, corrections, etc.)",
                approval_required=False,
                estimated_time_minutes=30,
                notes="Time varies by change scope",
            ),
            ReverseStep(
                step_number=5,
                action="Re-route for approval (full review cycle)",
                approval_required=False,
                estimated_time_minutes=10,
                notes="Document now goes through approval workflow again",
            ),
            ReverseStep(
                step_number=6,
                action="Log reversal in audit trail with reason",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_signed_to_approved(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """
        Steps to handle 'Signed' reversal (typically NOT PERMITTED per ISO).
        Included for completeness but should raise error in validate_state_transition.
        """
        return [
            ReverseStep(
                step_number=1,
                action="CONSTRAINT: Signed documents cannot be reverted",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=30,
                data_loss_risk="high",
                notes="Per ISO 9001:2015 §4.4.2, signed documents are historical records",
            ),
            ReverseStep(
                step_number=2,
                action="Alternative: Issue new document with corrections + obsolete old version",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=45,
                notes="Create change notice documenting why new version issued",
            ),
        ]

    def _build_rollback_path(self, from_state: str, to_state: str) -> str:
        """Build readable path description for reversal."""
        return f"{from_state} → {to_state}"

    def _get_dependencies(self, current_state: str) -> list[str]:
        """Get any dependencies for reversal from this state."""
        if current_state == "Approved":
            return [
                "Stakeholder notification (documented distribution list)",
                "Approval record (who approved initial version)",
            ]
        elif current_state == "Signed":
            return [
                "Quality manager approval",
                "Change control board review",
                "Document numbering system",
            ]
        return []

    def _get_constraints(self, current_state: str) -> list[str]:
        """Get regulatory/policy constraints for this reversal."""
        constraints = [
            "All reversals must be documented in audit trail per §8.5.2",
            "Change reason must be recorded",
        ]

        if current_state == "Signed":
            constraints.append("Signed documents cannot be modified—only obsoleted")
            constraints.append("New version must be issued if changes needed")

        return constraints
