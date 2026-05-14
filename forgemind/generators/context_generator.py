"""Generate .context files for AI agent instruction context."""

from __future__ import annotations

from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


class ContextGenerator(BaseGenerator):
    """Generate agent instruction context files."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        """Generate context data from project analysis."""
        context = {
            "project_name": analysis.metadata.name,
            "objective": analysis.input.objective,
            "constraints": analysis.input.constraints,
            "acceptance_criteria": analysis.acceptance_criteria,
            "top_risks": self._get_top_risks(analysis),
            "key_assumptions": self._get_key_assumptions(analysis),
            "human_review_gates": self._get_human_review_gates(analysis),
            "definition_of_done": self._get_definition_of_done(analysis),
            "rollback_plan": self._get_rollback_plan(analysis),
        }
        return context

    def _get_top_risks(self, analysis: ProjectAnalysis) -> list[dict]:
        """Extract top 3 risks with mitigation."""
        top_risks = sorted(
            analysis.risks,
            key=lambda r: (
                r.get("severity") == "High",
                r.get("probability") == "High",
            ),
            reverse=True,
        )[:3]
        return [
            {
                "risk": r.get("risk", "Unknown"),
                "mitigation": r.get("mitigation", "To be determined"),
                "owner": r.get("owner", "Unassigned"),
            }
            for r in top_risks
        ]

    def _get_key_assumptions(self, analysis: ProjectAnalysis) -> list[dict]:
        """Extract validation-critical assumptions."""
        critical = [a for a in analysis.assumptions if a.get("validation_needed")]
        return critical[:5]  # Top 5

    def _get_human_review_gates(self, analysis: ProjectAnalysis) -> list[str]:
        """Identify required human review gates from risks."""
        gates = []
        for risk in analysis.risks:
            if risk.get("human_review_required"):
                gates.append(risk.get("risk", "Review required"))
        return gates[:5]  # Top 5

    def _get_definition_of_done(self, analysis: ProjectAnalysis) -> list[str]:
        """Create definition of done from acceptance criteria."""
        dod = []
        for criterion in analysis.acceptance_criteria:
            dod.append(criterion.get("criterion", ""))
        return dod[:5]

    def _get_rollback_plan(self, analysis: ProjectAnalysis) -> str:
        """Extract rollback plan from control plan."""
        rollback_items = [
            item for item in analysis.control_plan
            if "rollback" in item.get("control_measure", "").lower()
        ]
        if rollback_items:
            return rollback_items[0].get("control_measure", "No rollback plan defined")
        return "No rollback plan defined"

    def _format_markdown_impl(self, data: dict) -> str:
        """Format context as Markdown."""
        lines = [
            f"# {data['project_name']} — Agent Instruction Context",
            "",
            "## Objective",
            data["objective"],
            "",
            "## Key Constraints",
            data["constraints"],
            "",
            "## Acceptance Criteria",
        ]

        for criterion in data["acceptance_criteria"][:3]:
            lines.append(f"- {criterion.get('criterion', 'Criterion')}")

        lines.extend([
            "",
            "## Top Risks & Mitigation",
        ])

        for risk in data["top_risks"]:
            lines.extend([
                f"### {risk['risk']}",
                f"- **Mitigation:** {risk['mitigation']}",
                f"- **Owner:** {risk['owner']}",
                "",
            ])

        lines.extend([
            "## Key Assumptions to Validate",
        ])

        for assumption in data["key_assumptions"]:
            lines.append(f"- {assumption.get('assumption', 'Assumption')}")

        lines.extend([
            "",
            "## Human Review Gates",
        ])

        for gate in data["human_review_gates"]:
            lines.append(f"- {gate}")

        lines.extend([
            "",
            "## Definition of Done",
        ])

        for dod in data["definition_of_done"]:
            lines.append(f"- [ ] {dod}")

        lines.extend([
            "",
            "## Rollback Plan",
            data["rollback_plan"],
        ])

        content = "\n".join(lines)
        return self.add_header(content)


def generate_context(analysis: ProjectAnalysis) -> str:
    """Convenience function to generate context markdown."""
    generator = ContextGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
