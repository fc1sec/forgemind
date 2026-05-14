"""
Software Engineering Reverse State Pattern.

Generic patterns for reverting software changes: Git, deployment, database
migrations. Two production-validated deployment variants are supported:

  - blue_green : two full environments + load-balancer switch
                 (Fowler — martinfowler.com/bliki/BlueGreenDeployment.html)
  - canary     : progressive traffic ramp with SLO-based auto-rollback
                 (Google SRE Workbook — sre.google/workbook/canarying-releases/)

ForgeMind does NOT redistribute upstream code. It codifies the published
patterns. See `forgemind/data/disciplines.yaml` for full attribution and the
decision criteria that distinguish the two variants.
"""

from typing import Any, Optional

from forgemind.schemas.project import ProjectAnalysis

from .reverse_state_pattern import (
    ReversalPlan,
    ReverseStateDefinition,
    ReverseStatePattern,
    ReverseStep,
)


class SoftwareReversePattern(ReverseStatePattern):
    """Software engineering reversal patterns (blue/green and canary)."""

    domain = "software"
    framework = "DevOps/SRE best practices (Fowler BlueGreen; Google SRE Workbook canarying)"
    description = (
        "Reversal patterns for code changes, deployments, and database migrations. "
        "Supports two production-validated deployment variants: blue/green (LB switch) "
        "and canary (progressive traffic ramp)."
    )

    # Variant identifiers — must match disciplines.yaml entries for `software`.
    VARIANT_BLUE_GREEN = "blue_green"
    VARIANT_CANARY = "canary"
    DEFAULT_VARIANT = VARIANT_BLUE_GREEN

    # Blue/Green machine — original 5-state model.
    # No explicit "Canary" tier; rollback is an instant LB switch.
    BLUE_GREEN_STATE_MACHINE = {
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

    # Canary machine — adds a `Canary` tier (1%-5% traffic slice) between
    # Staging and Production. Production rollback flows through Canary so
    # the rollback step is "drain traffic back through the canary tier"
    # rather than an instantaneous LB switch.
    CANARY_STATE_MACHINE = {
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
        "Canary": {
            "can_revert_to": ["Staging"],
            "reversible": True,
            "data_loss": "low",
        },
        "Production": {
            "can_revert_to": ["Canary"],
            "reversible": True,
            "data_loss": "medium",
        },
    }

    # Mapping variant id → state machine. Add new variants here AND in
    # disciplines.yaml so the consultant can offer them.
    VARIANTS = {
        VARIANT_BLUE_GREEN: BLUE_GREEN_STATE_MACHINE,
        VARIANT_CANARY: CANARY_STATE_MACHINE,
    }

    # The legacy attribute name STATE_MACHINE remains for backward compatibility
    # with code/tests that read it directly. It mirrors the default variant.
    STATE_MACHINE = BLUE_GREEN_STATE_MACHINE

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, variant_id: Optional[str] = None) -> None:
        """Construct a software plugin bound to a deployment variant.

        Args:
            variant_id: One of the VARIANTS keys. Defaults to blue/green.
        """
        self.variant_id = variant_id or self.DEFAULT_VARIANT
        if self.variant_id not in self.VARIANTS:
            raise ValueError(
                f"Unknown software variant: {self.variant_id}. "
                f"Known: {sorted(self.VARIANTS.keys())}"
            )
        # Bind the active machine on the instance so it shadows the
        # class-level STATE_MACHINE attribute used below.
        self.STATE_MACHINE = self.VARIANTS[self.variant_id]

    def get_supported_states(self) -> list[ReverseStateDefinition]:
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

        # Determine steps based on state pair. Production rollback steps
        # differ between blue/green and canary variants.
        if current_state == "In Code Review" and target_state == "In Development":
            steps = self._steps_review_to_dev()
        elif current_state == "Merged to Main" and target_state == "In Code Review":
            steps = self._steps_merged_to_review()
        elif current_state == "Staging" and target_state == "In Code Review":
            steps = self._steps_staging_to_review()
        elif current_state == "Canary" and target_state == "Staging":
            steps = self._steps_canary_to_staging()
        elif current_state == "Production" and target_state == "Canary":
            steps = self._steps_prod_to_canary()
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

    def _steps_review_to_dev(self) -> list[ReverseStep]:
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

    def _steps_merged_to_review(self) -> list[ReverseStep]:
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

    def _steps_staging_to_review(self) -> list[ReverseStep]:
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

    def _steps_prod_to_staging(self) -> list[ReverseStep]:
        """Revert from production directly to staging (blue/green variant).

        Blue/green semantics: an instant LB switch returns 100% of traffic to
        the prior (blue) environment. No progressive ramp.
        """
        return [
            ReverseStep(
                step_number=1,
                action="Switch load balancer to blue environment (previous version)",
                approval_required=True,
                approval_role="on_call_engineer",
                estimated_time_minutes=2,
                data_loss_risk="none",
                notes="Assumes blue/green deployment setup; rollback is instantaneous",
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

    def _steps_prod_to_canary(self) -> list[ReverseStep]:
        """Revert from full production to the canary tier (canary variant).

        Canary semantics: drain traffic from the new revision back through
        the canary tier (e.g. 100% → 10% → 0%) using the platform's
        traffic-shaping mechanism (Istio, Linkerd, Argo Rollouts, Flagger).
        """
        return [
            ReverseStep(
                step_number=1,
                action="SRE / release manager approves progressive rollback decision",
                approval_required=True,
                approval_role="sre_release_manager",
                estimated_time_minutes=5,
                notes="Canary rollback is reversible mid-flight; document the trigger metric",
            ),
            ReverseStep(
                step_number=2,
                action="Shift traffic weights: new revision 100% → 50% → 10% → 0%",
                approval_required=False,
                estimated_time_minutes=10,
                notes="Use service mesh / LB weights (Istio, Argo Rollouts, Flagger)",
            ),
            ReverseStep(
                step_number=3,
                action="Verify SLO recovery at each weight step (latency, error rate)",
                approval_required=False,
                estimated_time_minutes=10,
                notes="Kayenta-style canary analysis recommended for objective gating",
            ),
            ReverseStep(
                step_number=4,
                action="Drain remaining sessions on the new revision",
                approval_required=False,
                estimated_time_minutes=5,
                data_loss_risk="low",
                notes="In-flight sessions may experience brief disruption",
            ),
            ReverseStep(
                step_number=5,
                action="Confirm SLO recovered; record incident postmortem note",
                approval_required=False,
                estimated_time_minutes=10,
            ),
        ]

    def _steps_canary_to_staging(self) -> list[ReverseStep]:
        """Revert from canary tier back to staging (canary variant).

        At canary, only a small traffic slice sees the new revision. Rollback
        is fast: cut the canary weight to zero, then push the canary tier
        back to staging-equivalent state.
        """
        return [
            ReverseStep(
                step_number=1,
                action="Cut canary traffic weight to 0% (kill canary)",
                approval_required=False,
                estimated_time_minutes=1,
                notes="Affected user slice was 1%-5%; blast radius limited by design",
            ),
            ReverseStep(
                step_number=2,
                action="Verify baseline SLO returned (latency, error rate)",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Remove the canary deployment from the cluster",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=4,
                action="Open follow-up issue with the trigger metric for root-cause analysis",
                approval_required=False,
                estimated_time_minutes=10,
            ),
        ]

    def _get_dependencies(self, current_state: str) -> list[str]:
        """Get dependencies for reversal (variant-aware)."""
        deps = ["Git repository with commit history"]
        if current_state == "Production":
            if self.variant_id == self.VARIANT_CANARY:
                deps.extend([
                    "Canary deployment controller (Argo Rollouts / Flagger / Spinnaker)",
                    "Service mesh or LB capable of weighted traffic shifting (Istio / Linkerd / Envoy / NGINX)",
                    "SLO-based metric provider (Prometheus / Datadog / NewRelic) for rollback gating",
                ])
            else:  # blue/green default
                deps.extend([
                    "Blue/green deployment infrastructure (two production environments)",
                    "Load balancer or DNS capable of an instantaneous traffic switch",
                    "Monitoring and alerting",
                ])
        if current_state == "Canary":
            deps.extend([
                "Canary deployment controller",
                "SLO metric provider for rollback gating",
            ])
        if current_state in ["Production", "Canary", "Staging"]:
            deps.append("Database backup before migration")
        return deps

    def _get_constraints(self, current_state: str) -> list[str]:
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
