"""
AI/ML Reverse State Pattern.

Two production-validated deployment variants are supported:

  - feature_flag_checkpoint : Canary tier + feature-flag traffic shifting;
                              rollback via flag flip and checkpoint restore.
                              Source: MLOps community (MLflow, LaunchDarkly,
                              KServe, TF Serving practices).
  - shadow_deployment       : New model runs in parallel; only the old model
                              serves users; shadow predictions logged for
                              offline analysis. Rollback from Production is
                              an instant swap; rollback from Shadow is just
                              turning off the shadow logger (zero user impact).
                              Source: Sculley et al., "Hidden Technical Debt
                              in ML Systems" (NeurIPS 2015); Sato et al.,
                              "Continuous Delivery for Machine Learning"
                              (martinfowler.com, 2019); Netflix Tech Blog.

ForgeMind codifies the patterns. No upstream code is redistributed.
"""

from typing import Any, Optional

from forgemind.schemas.project import ProjectAnalysis

from .reverse_state_pattern import (
    ReversalPlan,
    ReverseStateDefinition,
    ReverseStatePattern,
    ReverseStep,
)


class AIMLReversePattern(ReverseStatePattern):
    """AI/ML model deployment reversal patterns (feature-flag and shadow)."""

    domain = "ai_ml"
    framework = "MLOps/AI best practices (Sculley 2015, Sato 2019, Netflix)"
    description = (
        "Reversal patterns for model deployments, feature flags, and data migrations. "
        "Two variants: feature-flag/checkpoint and shadow deployment."
    )

    VARIANT_FEATURE_FLAG_CHECKPOINT = "feature_flag_checkpoint"
    VARIANT_SHADOW_DEPLOYMENT = "shadow_deployment"
    DEFAULT_VARIANT = VARIANT_FEATURE_FLAG_CHECKPOINT

    # Feature-flag + checkpoint variant (original 4-state machine).
    # Rollback uses traffic shifting via feature flags.
    FEATURE_FLAG_STATE_MACHINE = {
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

    # Shadow deployment variant — new model runs in parallel with current
    # production; both receive real traffic, but only the production model's
    # predictions reach users. Shadow predictions are logged for offline
    # comparison. Rollback from Shadow is zero-user-impact (just turn off the
    # logger). Promotion to Production swaps which model serves users.
    SHADOW_STATE_MACHINE = {
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
        "Shadow": {
            "can_revert_to": ["Validation"],
            "reversible": True,
            "data_loss": "none",  # users never saw shadow predictions
        },
        "Production": {
            "can_revert_to": ["Shadow"],
            "reversible": True,
            "data_loss": "low",  # swap is instant; only in-flight requests
        },
    }

    # Mapping variant id → state machine.
    VARIANTS = {
        VARIANT_FEATURE_FLAG_CHECKPOINT: FEATURE_FLAG_STATE_MACHINE,
        VARIANT_SHADOW_DEPLOYMENT: SHADOW_STATE_MACHINE,
    }

    # Legacy attribute name preserved for backward compatibility (defaults
    # to feature_flag_checkpoint, the prior canonical machine).
    STATE_MACHINE = FEATURE_FLAG_STATE_MACHINE

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, variant_id: Optional[str] = None) -> None:
        """Construct an AI/ML plugin bound to a deployment variant.

        Args:
            variant_id: One of the VARIANTS keys. Defaults to
                feature_flag_checkpoint (the prior canonical pattern).
        """
        self.variant_id = variant_id or self.DEFAULT_VARIANT
        if self.variant_id not in self.VARIANTS:
            raise ValueError(
                f"Unknown ai_ml variant: {self.variant_id}. "
                f"Known: {sorted(self.VARIANTS.keys())}"
            )
        self.STATE_MACHINE = self.VARIANTS[self.variant_id]

    def get_supported_states(self) -> list[ReverseStateDefinition]:
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

    def validate_state_transition(self, from_state: str, to_state: str) -> dict[str, Any]:
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

        # Determine steps. Shadow variant uses different rollback semantics
        # than the feature-flag/checkpoint variant.
        if current_state == "Validation" and target_state == "Model Training":
            steps = self._steps_validation_to_training()
        elif current_state == "Staging (Canary)" and target_state == "Validation":
            steps = self._steps_canary_to_validation()
        elif current_state == "Production" and target_state == "Staging (Canary)":
            steps = self._steps_prod_to_canary()
        elif current_state == "Shadow" and target_state == "Validation":
            steps = self._steps_shadow_to_validation()
        elif current_state == "Production" and target_state == "Shadow":
            steps = self._steps_prod_to_shadow()
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

    def _steps_validation_to_training(self) -> list[ReverseStep]:
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

    def _steps_canary_to_validation(self) -> list[ReverseStep]:
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

    def _steps_prod_to_canary(self) -> list[ReverseStep]:
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

    # Shadow-variant step builders -------------------------------------

    def _steps_shadow_to_validation(self) -> list[ReverseStep]:
        """Stop shadowing (zero user impact) and return to validation.

        Shadow predictions never reached users, so the rollback is purely
        operational: turn off the shadow logger and inspect the collected
        predictions to understand WHY shadow was rolled back.
        """
        return [
            ReverseStep(
                step_number=1,
                action="Disable the shadow model in the serving plane (stop receiving traffic)",
                approval_required=False,
                estimated_time_minutes=2,
                notes="No user impact — only the production model served predictions",
            ),
            ReverseStep(
                step_number=2,
                action="Stop logging shadow predictions; archive the predictions collected so far",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Run offline comparison on the collected shadow vs production predictions",
                approval_required=False,
                estimated_time_minutes=30,
                notes="The point of shadowing — diagnose why the new model wasn't ready",
            ),
            ReverseStep(
                step_number=4,
                action="Document findings; return the model to Validation with corrective changes",
                approval_required=False,
                estimated_time_minutes=15,
            ),
        ]

    def _steps_prod_to_shadow(self) -> list[ReverseStep]:
        """Demote a production model back to shadow.

        With shadow deployment, promotion to Production = swap which model
        serves users. Rollback = swap back. Because both models stay
        running side-by-side, the swap is near-instantaneous; the only
        in-flight impact is the brief request-routing transition.
        """
        return [
            ReverseStep(
                step_number=1,
                action="ML-ops on-call approves the swap-back decision",
                approval_required=True,
                approval_role="ml_ops_oncall",
                estimated_time_minutes=5,
                notes="Document the trigger metric (accuracy drop, latency spike, etc.)",
            ),
            ReverseStep(
                step_number=2,
                action="Swap serving roles: previous model returns to Production; new model returns to Shadow",
                approval_required=False,
                estimated_time_minutes=2,
                data_loss_risk="low",
                notes="In-flight requests may experience a brief routing transition",
            ),
            ReverseStep(
                step_number=3,
                action="Verify the previous model is serving and SLO metrics are recovering",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=4,
                action="Re-enable shadow logging on the demoted model for forensic analysis",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=5,
                action="Open incident report with the demotion trigger and shadow comparison data",
                approval_required=False,
                estimated_time_minutes=15,
            ),
        ]

    def _get_dependencies(self, current_state: str) -> list[str]:
        """Get dependencies for reversal (variant-aware)."""
        deps = [
            "Model versioning system (MLflow, Weights & Biases, etc.)",
            "Checkpoint/model registry with accessible prior versions",
        ]
        if self.variant_id == self.VARIANT_SHADOW_DEPLOYMENT:
            deps.extend([
                "Shadow-mode serving infrastructure (dual-model deployment)",
                "Prediction comparison / divergence-analysis tooling",
            ])
        else:
            deps.append("Feature flag system (LaunchDarkly, custom, etc.)")

        if current_state in ["Staging (Canary)", "Production", "Shadow"]:
            deps.extend([
                "Inference API compatible with previous model version",
                "Serving infrastructure (TensorFlow Serving, KServe, etc.)",
                "Monitoring dashboard for model metrics",
            ])

        return deps

    def _get_constraints(self, current_state: str) -> list[str]:
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
