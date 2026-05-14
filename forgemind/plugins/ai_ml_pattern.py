"""
AI/ML Reverse State Pattern

Patterns for reverting model deployments, feature flags, and checkpoints.
"""

from typing import Dict, List, Optional, Any
from .reverse_state_pattern import (
    ReverseStatePattern,
    ReverseStateDefinition,
    ReverseStep,
    ReversalPlan,
)
from forgemind.schemas.project import ProjectAnalysis


class AIMLReversePattern(ReverseStatePattern):
    """AI/ML model and feature reversal patterns."""

    domain = "ai_ml"
    framework = "MLOps/AI best practices"
    description = (
        "Reversal patterns for model deployments, feature flags, and data migrations. "
        "Focuses on model versioning, checkpoint restore, and gradual rollback strategies."
    )

    STATE_MACHINE = {
        "Model Training": {
            "can_revert_to": [],
            "reversible": True,
            "data_loss": "none",
        },
        "Validation": {
            "can_revert_to": ["Model Training"],
            "reversible": True,
            "data_loss": "none",
        },
        "Staging (Canary)": {
            "can_revert_to": ["Validation"],
            "reversible": True,
            "data_loss": "low",
        },
        "Production": {
            "can_revert_to": ["Staging (Canary)"],
            "reversible": True,
            "data_loss": "medium",
        },
    }

    def get_supported_states(self) -> List[ReverseStateDefinition]:
        """Return AI/ML deployment states."""
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
        """Generate AI/ML reversal plan."""

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

        # Determine steps
        if current_state == "Validation" and target_state == "Model Training":
            steps = self._steps_validation_to_training()
        elif current_state == "Staging (Canary)" and target_state == "Validation":
            steps = self._steps_canary_to_validation()
        elif current_state == "Production" and target_state == "Staging (Canary)":
            steps = self._steps_prod_to_canary()
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
            approval_gates=["ml_ops"] if validation.get("requires_approval") else [],
            dependencies=self._get_dependencies(current_state),
            constraints=self._get_constraints(current_state),
            confidence=0.85,  # Slightly lower due to model-specific unknowns
        )

    def _steps_validation_to_training(self) -> List[ReverseStep]:
        """Revert from validation back to retraining."""
        return [
            ReverseStep(
                step_number=1,
                action="Load previous training checkpoint",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=2,
                action="Document validation failure reason",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=3,
                action="Identify retraining changes (data, hyperparameters, features)",
                approval_required=False,
                estimated_time_minutes=30,
            ),
        ]

    def _steps_canary_to_validation(self) -> List[ReverseStep]:
        """Revert from canary deployment."""
        return [
            ReverseStep(
                step_number=1,
                action="Disable feature flag or reduce traffic to <1%",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=2,
                action="Collect metrics on canary performance",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=3,
                action="Restore traffic to previous model version",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=4,
                action="Verify performance metrics return to baseline",
                approval_required=False,
                estimated_time_minutes=15,
            ),
        ]

    def _steps_prod_to_canary(self) -> List[ReverseStep]:
        """Revert from production deployment."""
        return [
            ReverseStep(
                step_number=1,
                action="Activate feature flag: Route 5% traffic to previous model",
                approval_required=True,
                approval_role="ml_ops_oncall",
                estimated_time_minutes=2,
                data_loss_risk="none",
            ),
            ReverseStep(
                step_number=2,
                action="Monitor metrics for 10 minutes",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=3,
                action="If no issues: Scale back to 100% previous model",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=4,
                action="Run inference accuracy audit (sample predictions)",
                approval_required=False,
                estimated_time_minutes=30,
                data_loss_risk="low",
            ),
        ]

    def _get_dependencies(self, current_state: str) -> List[str]:
        """Get dependencies for reversal."""
        deps = [
            "Model versioning system (MLflow, Weights & Biases, etc.)",
            "Checkpoint/model registry with accessible prior versions",
            "Feature flag system (LaunchDarkly, custom, etc.)",
        ]

        if current_state in ["Staging (Canary)", "Production"]:
            deps.extend([
                "Inference API compatible with previous model version",
                "Serving infrastructure (TensorFlow Serving, KServe, etc.)",
                "Monitoring dashboard for model metrics",
            ])

        return deps

    def _get_constraints(self, current_state: str) -> List[str]:
        """Get constraints for reversal."""
        constraints = []

        if current_state == "Production":
            constraints.extend([
                "10-minute SLA for critical model rollback",
                "Customer impact assessment required",
                "Data validation audit required before re-enabling new model",
            ])

        constraints.extend([
            "Previous model version must have been tested and validated",
            "Model serving infrastructure must support version switching",
            "Inference latency may differ between model versions",
        ])

        return constraints
