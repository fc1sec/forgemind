"""
Software Engineering Reverse State Pattern

Generic patterns for reverting software changes: Git, deployment, database migrations.
"""

from typing import Dict, List, Optional, Any
from .reverse_state_pattern import (
    ReverseStatePattern,
    ReverseStateDefinition,
    ReverseStep,
    ReversalPlan,
)
from forgemind.schemas.project import ProjectAnalysis


class SoftwareReversePattern(ReverseStatePattern):
    """Software engineering reversal patterns."""

    domain = "software"
    framework = "DevOps/SRE best practices"
    description = (
        "Reversal patterns for code changes, deployments, and database migrations. "
        "Focuses on Git workflows, blue-green deployments, and database rollback."
    )

    STATE_MACHINE = {
        "In Development": {
            "can_revert_to": [],
            "reversible": True,
            "data_loss": "none",
        },
        "In Code Review": {
            "can_revert_to": ["In Development"],
            "reversible": True,
            "data_loss": "none",
        },
        "Merged to Main": {
            "can_revert_to": ["In Code Review"],
            "reversible": True,
            "data_loss": "none",
        },
        "Staging": {
            "can_revert_to": ["In Code Review"],
            "reversible": True,
            "data_loss": "low",
        },
        "Production": {
            "can_revert_to": ["Staging"],
            "reversible": True,
            "data_loss": "medium",
        },
    }

    def get_supported_states(self) -> List[ReverseStateDefinition]:
        """Return software development states."""
        definitions = []
        for state_name, config in self.STATE_MACHINE.items():
            definitions.append(
                ReverseStateDefinition(
                    state_name=state_name,
                    can_revert_to=config["can_revert_to"],
                    reversible=config["reversible"],
                    data_loss=config.get("data_loss", "none"),
                )
            )
        return definitions

    def validate_state_transition(self, from_state: str, to_state: str) -> Dict[str, Any]:
        """Check if state transition is valid."""
        if from_state not in self.STATE_MACHINE:
            return {"is_valid": False, "reason": f"Unknown state: {from_state}"}

        if to_state not in self.STATE_MACHINE[from_state]["can_revert_to"]:
            return {
                "is_valid": False,
                "reason": f"Cannot revert from {from_state} to {to_state}",
            }

        return {"is_valid": True, "requires_approval": from_state == "Production"}

    def generate_reversal_plan(
        self,
        project: ProjectAnalysis,
        current_state: str,
        target_state: Optional[str] = None,
    ) -> ReversalPlan:
        """Generate software reversal plan."""

        if current_state not in self.STATE_MACHINE:
            raise ValueError(f"Unknown state: {current_state}")

        if target_state is None:
            possible = self.STATE_MACHINE[current_state]["can_revert_to"]
            if not possible:
                raise ValueError(f"Cannot revert from {current_state}")
            target_state = possible[0]

        validation = self.validate_state_transition(current_state, target_state)
        if not validation["is_valid"]:
            raise ValueError(validation["reason"])

        # Determine steps based on state pair
        if current_state == "In Code Review" and target_state == "In Development":
            steps = self._steps_review_to_dev()
        elif current_state == "Merged to Main" and target_state == "In Code Review":
            steps = self._steps_merged_to_review()
        elif current_state == "Staging" and target_state == "In Code Review":
            steps = self._steps_staging_to_review()
        elif current_state == "Production" and target_state == "Staging":
            steps = self._steps_prod_to_staging()
        else:
            steps = []

        total_time = sum(s.estimated_time_minutes or 0 for s in steps)
        risks = [s.data_loss_risk for s in steps if s.data_loss_risk != "none"]
        highest_risk = max(risks) if risks else "none"

        return ReversalPlan(
            current_state=current_state,
            target_state=target_state,
            rollback_path=f"{current_state} → {target_state}",
            steps=steps,
            total_estimated_time_minutes=total_time,
            highest_data_loss_risk=highest_risk,
            approval_gates=["code_review"] if validation.get("requires_approval") else [],
            dependencies=self._get_dependencies(current_state),
            constraints=self._get_constraints(current_state),
            confidence=0.90,
        )

    def _steps_review_to_dev(self) -> List[ReverseStep]:
        """Revert from code review to development."""
        return [
            ReverseStep(
                step_number=1,
                action="Close or mark PR as abandoned",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=2,
                action="Delete remote branch (optional)",
                approval_required=False,
                estimated_time_minutes=2,
            ),
        ]

    def _steps_merged_to_review(self) -> List[ReverseStep]:
        """Revert merged code via git revert."""
        return [
            ReverseStep(
                step_number=1,
                action="Create new PR with: git revert <commit-hash>",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=2,
                action="Code review of revert",
                approval_required=True,
                approval_role="code_reviewer",
                estimated_time_minutes=15,
            ),
            ReverseStep(
                step_number=3,
                action="Merge revert PR",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_staging_to_review(self) -> List[ReverseStep]:
        """Revert from staging."""
        return [
            ReverseStep(
                step_number=1,
                action="Revert commit in staging branch",
                approval_required=False,
                estimated_time_minutes=10,
                notes="git revert or reset depending on workflow",
            ),
            ReverseStep(
                step_number=2,
                action="Run tests on staging to verify revert",
                approval_required=False,
                estimated_time_minutes=20,
            ),
        ]

    def _steps_prod_to_staging(self) -> List[ReverseStep]:
        """Revert from production (blue-green deployment)."""
        return [
            ReverseStep(
                step_number=1,
                action="Switch load balancer to blue environment (previous version)",
                approval_required=True,
                approval_role="on_call_engineer",
                estimated_time_minutes=2,
                data_loss_risk="none",
                notes="Assumes blue-green deployment setup",
            ),
            ReverseStep(
                step_number=2,
                action="Verify health checks pass on blue",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Monitor for issues (5-10 min)",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=4,
                action="Deploy hotfix to green if needed",
                approval_required=False,
                estimated_time_minutes=30,
                data_loss_risk="low",
                notes="For data-corruption issues",
            ),
        ]

    def _get_dependencies(self, current_state: str) -> List[str]:
        """Get dependencies for reversal."""
        deps = ["Git repository with commit history"]
        if current_state == "Production":
            deps.extend([
                "Blue-green or canary deployment infrastructure",
                "Load balancer configured for traffic switching",
                "Monitoring and alerting",
            ])
        if current_state in ["Production", "Staging"]:
            deps.append("Database backup before migration")
        return deps

    def _get_constraints(self, current_state: str) -> List[str]:
        """Get constraints for reversal."""
        constraints = []
        if current_state == "Production":
            constraints.extend([
                "15-minute SLA for critical rollbacks",
                "Customer impact assessment required",
                "Incident communication required",
            ])
        if current_state in ["Production", "Staging"]:
            constraints.append("Database migrations may not be fully reversible")
        return constraints
