"""Generate reversal/rollback plans using domain-specific plugins (v1.2.0)."""

from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis
from forgemind.plugins import get_plugin_registry
from forgemind.epistemics import EpistemicValidator, OutputClassification


class ReverseContextGenerator(BaseGenerator):
    """Generate reversal/rollback plans from reverse state machine plugins."""

    def __init__(self):
        """Initialize generator with plugin registry and epistemic validator."""
        self.plugin_registry = get_plugin_registry()
        self.epistemic_validator = EpistemicValidator(self.plugin_registry)

    def generate(self, analysis: ProjectAnalysis) -> dict:
        """
        Generate reversal plan data from project analysis.

        Returns dict with:
        - plugin_domain: Domain of plugin used
        - plugin_available: Whether plugin exists for domain
        - current_state: Current project state
        - reversal_available: Whether reversal is possible
        - reversal_plan: ReversalPlan object (if available)
        - escalation: Escalation info (if needed)
        - epistemic_classification: DETERMINISTIC/STOCHASTIC/ESCALATE
        - confidence: Confidence score 0.0-1.0
        """
        domain = analysis.metadata.domain
        current_state = analysis.input.current_state

        result = {
            "project_name": analysis.metadata.name,
            "domain": domain,
            "current_state": current_state or "Unknown",
            "plugin_available": self.plugin_registry.has_pattern(domain),
            "reversal_plan": None,
            "escalation_needed": False,
            "escalate_to": None,
            "epistemic_classification": None,
            "confidence": 0.0,
            "message": "",
        }

        # Layer 1: Check if plugin exists for domain
        if not result["plugin_available"]:
            result["escalation_needed"] = True
            result["escalate_to"] = self._get_escalation_contact(domain)
            result["message"] = f"Domain '{domain}' does not have a reverse pattern plugin yet."
            result["epistemic_classification"] = "ESCALATE"
            return result

        # Layer 2: Get plugin and attempt reversal plan generation
        try:
            plugin = self.plugin_registry.get_pattern(domain)
            if current_state:
                reversal_plan = plugin.generate_reversal_plan(
                    project=analysis,
                    current_state=current_state
                )
                result["reversal_plan"] = reversal_plan
            else:
                result["message"] = "Current state not specified in project input"
                return result

        except ValueError as e:
            result["escalation_needed"] = True
            result["message"] = f"Reversal not possible: {str(e)}"
            result["epistemic_classification"] = "ESCALATE"
            return result

        # Layer 3: Validate output through epistemic validator
        reversal_plan = result["reversal_plan"]
        plan_summary = self._summarize_plan(reversal_plan)

        validation = self.epistemic_validator.validate_output(
            output_text=plan_summary,
            confidence=reversal_plan.confidence,
            domain=domain,
            sources=["expert_plugin"]  # Plugin is expert-contributed
        )

        result["epistemic_classification"] = validation.classification.name
        result["confidence"] = validation.confidence
        result["message"] = validation.message
        result["escalation_needed"] = validation.escalation_needed
        result["escalate_to"] = validation.escalate_to

        # Add confidence label if stochastic
        if validation.requires_label:
            result["confidence_label"] = validation.suggested_label

        return result

    def _summarize_plan(self, reversal_plan) -> str:
        """Create text summary of reversal plan for epistemic validation."""
        lines = [
            f"Reversal from {reversal_plan.current_state} to {reversal_plan.target_state}",
            f"Time estimate: {reversal_plan.total_estimated_time_minutes} minutes",
            f"Data loss risk: {reversal_plan.highest_data_loss_risk}",
        ]
        return "\n".join(lines)

    def _get_escalation_contact(self, domain: str) -> str:
        """Get escalation contact for domain."""
        contacts = {
            "iso9001": "QMS expert / ISO auditor",
            "software": "DevOps / SRE engineer",
            "ai_ml": "ML Ops / ML Engineer",
            "tender": "Government contracts specialist",
            "hardware_firmware": "Embedded systems engineer",
            "biomedical_device": "Biomedical engineer / FDA specialist",
        }
        return contacts.get(domain, "Domain expert")

    def _format_markdown_impl(self, data: dict) -> str:
        """Format reversal plan as Markdown."""
        lines = [
            f"# {data['project_name']} — Reversal & Rollback Plan",
            "",
            f"**Domain:** {data['domain']}  ",
            f"**Current State:** {data['current_state']}  ",
            f"**Classification:** {data['epistemic_classification']}  ",
            f"**Confidence:** {data['confidence']:.0%}",
            "",
        ]

        # If plugin not available
        if not data["plugin_available"]:
            lines.extend([
                "## ⚠️ Reversal Pattern Not Available",
                "",
                f"The '{data['domain']}' domain does not yet have a reverse state pattern in ForgeMind.",
                "",
                f"**Escalate to:** {data['escalate_to']}",
                "",
                "**Why?** ForgeMind does not invent reversal patterns—it codifies expert knowledge. "
                "To contribute a pattern for this domain, see CONTRIBUTING_REVERSE_PATTERNS.md",
                "",
                "**What to do:**",
                "1. Consult with domain expert or review official standards",
                "2. Document realistic reversal constraints and processes",
                "3. Submit pattern via https://github.com/forgemind/forgemind/issues/new?template=pattern-contribution.md",
                "",
            ])
        # If reversal not possible from current state
        elif not data["reversal_plan"]:
            lines.extend([
                "## ❌ Reversal Not Possible from This State",
                "",
                data["message"],
                "",
            ])
        # If reversal is possible
        else:
            plan = data["reversal_plan"]
            lines.extend([
                f"## Rollback Path",
                "",
                f"`{plan.rollback_path}`",
                "",
            ])

            # Time estimate
            lines.extend([
                "## Time Estimate",
                "",
                f"**Total:** {plan.total_estimated_time_minutes} minutes",
                "",
            ])

            # Data loss risk
            lines.extend([
                "## Data Loss Risk",
                "",
                f"**Highest Risk Level:** {plan.highest_data_loss_risk}",
                "",
            ])

            # Approval gates
            if plan.approval_gates:
                lines.extend([
                    "## Approval Gates Required",
                    "",
                ])
                for gate in plan.approval_gates:
                    lines.append(f"- {gate}")
                lines.append("")

            # Reversal steps
            if plan.steps:
                lines.extend([
                    "## Reversal Steps",
                    "",
                ])
                for step in plan.steps:
                    approval_marker = "🔒" if step.approval_required else "✓"
                    lines.extend([
                        f"### Step {step.step_number}: {approval_marker} {step.action}",
                        "",
                    ])
                    if step.estimated_time_minutes:
                        lines.append(
                            f"**Time:** {step.estimated_time_minutes} min"
                        )
                    if step.approval_required:
                        role = getattr(step, 'approval_role', 'approver')
                        lines.append(f"**Approval Required:** {role}")
                    if step.data_loss_risk != "none":
                        lines.append(f"**Data Loss Risk:** {step.data_loss_risk}")
                    if getattr(step, 'notes', None):
                        lines.append(f"**Notes:** {step.notes}")
                    lines.append("")

            # Dependencies
            if plan.dependencies:
                lines.extend([
                    "## Dependencies",
                    "",
                    "Reversal requires the following systems/tools to be in place:",
                    "",
                ])
                for dep in plan.dependencies:
                    lines.append(f"- {dep}")
                lines.append("")

            # Constraints
            if plan.constraints:
                lines.extend([
                    "## Constraints & Limitations",
                    "",
                ])
                for constraint in plan.constraints:
                    lines.append(f"- {constraint}")
                lines.append("")

        # Epistemic classification footer
        lines.extend([
            "---",
            "",
            "## Epistemic Classification",
            "",
        ])

        if data["epistemic_classification"] == "DETERMINISTIC":
            lines.append(
                "**DETERMINISTIC:** This reversal pattern is based on official standards "
                "or expert-contributed domain knowledge. High confidence."
            )
        elif data["epistemic_classification"] == "STOCHASTIC":
            lines.extend([
                "**STOCHASTIC (Empirical):** This pattern is based on real-world outcomes "
                f"from similar projects. Confidence: {data['confidence']:.0%}",
                "",
                "This is NOT a certainty—it's an empirical pattern. Verify with domain "
                "expert before relying on this approach.",
            ])
            if data.get("confidence_label"):
                lines.append("")
                lines.append(data["confidence_label"])
        elif data["epistemic_classification"] == "ESCALATE":
            lines.extend([
                "**OUT OF SCOPE:** This domain is not yet supported by ForgeMind, or the "
                "reversal is not feasible from the current state.",
                "",
                f"Escalate to: **{data['escalate_to']}**",
            ])

        lines.extend([
            "",
            "---",
            "Generated by ForgeMind v1.2.0",
            "This output is a readiness aid, not a certification or compliance guarantee.",
        ])

        content = "\n".join(lines)
        return content


def generate_reverse_context(analysis: ProjectAnalysis) -> str:
    """Convenience function to generate reversal plan markdown."""
    generator = ReverseContextGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
