"""Generate AI-specific risk readiness checklists."""

from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


class AIRiskChecklistGenerator(BaseGenerator):
    """Generate domain-specific AI risk checklists."""

    # Domain-specific risk patterns
    DOMAIN_PATTERNS = {
        "ai_project": [
            "Agent has explicit boundary definitions (scope, tools, decision authority)",
            "Unsafe operations identified and explicitly locked down",
            "Tool permission matrix exists (allowed vs. denied operations)",
            "Rollback plan is executable in <10 minutes",
            "Human review gates defined for: code modification, API calls, external resources",
            "Assumption validation plan exists (especially for agent capabilities)",
            "Test harness exists to validate boundary compliance",
            "Agent output validation (format, safety checks) implemented",
            "Audit trail mechanism for all agent decisions",
            "Stakeholder alignment on risk tolerance and approval process",
        ],
        "software_project": [
            "Code review process documented and enforced",
            "Test coverage target >80% for new code",
            "Security dependencies audited (OWASP, CVE checks)",
            "Database migration rollback plan tested",
            "Deployment rollback defined (<15 min window)",
            "Performance requirements documented and validated",
            "Error handling for external service failures",
            "Data privacy/compliance requirements clear",
            "Monitoring and alerting configured before prod",
            "Change management approval gates in place",
        ],
        "qms_iso": [
            "Process documentation complete and current",
            "Evidence requirements identified for audit",
            "Control points mapped to ISO requirements",
            "Training/competency requirements defined",
            "Risk assessment completed (FMEA or similar)",
            "Non-conformance handling procedure exists",
            "Management review schedule established",
            "Internal audit plan created",
            "Traceability matrix complete",
            "Retention policy for required records",
        ],
        "generic": [
            "Objective clearly defined and measurable",
            "Success criteria documented and testable",
            "Risks identified and mitigation assigned",
            "Assumptions documented and validation planned",
            "Stakeholder communication plan exists",
            "Resource availability confirmed",
            "Timeline realistic and achievable",
            "Scope controls in place to prevent creep",
            "Quality acceptance criteria defined",
            "Contingency plan for critical failures",
        ],
    }

    def generate(self, analysis: ProjectAnalysis) -> dict:
        """Generate AI risk checklist for domain."""
        domain = analysis.metadata.domain
        checklist = self.DOMAIN_PATTERNS.get(domain, self.DOMAIN_PATTERNS["generic"])

        # Score against existing risks
        scored_items = self._score_checklist(checklist, analysis)

        return {
            "domain": domain,
            "project": analysis.metadata.name,
            "items": scored_items,
            "completed_count": sum(1 for item in scored_items if item["status"] == "✓"),
            "total_count": len(scored_items),
        }

    def _score_checklist(self, checklist: list[str], analysis: ProjectAnalysis) -> list[dict]:
        """Score checklist items against existing analysis."""
        scored = []
        risk_texts = " ".join(r.get("risk", "") for r in analysis.risks).lower()
        control_texts = " ".join(c.get("control_measure", "") for c in analysis.control_plan).lower()

        for item in checklist:
            item_lower = item.lower()
            # Simple heuristic: if item keywords appear in risks/controls, mark as addressed
            keywords = item_lower.split()[:3]
            found = any(keyword in risk_texts or keyword in control_texts for keyword in keywords)

            scored.append({
                "item": item,
                "status": "✓" if found else "⚠",
                "addressed": found,
            })

        return scored

    def _format_markdown_impl(self, data: dict) -> str:
        """Format checklist as Markdown."""
        lines = [
            f"# {data['project']} — AI Risk Readiness Checklist",
            f"Domain: {data['domain'].replace('_', ' ').title()}",
            "",
            f"## Progress: {data['completed_count']}/{data['total_count']} items addressed",
            "",
            "## Checklist",
            "",
        ]

        for item in data["items"]:
            status = "✅" if item["addressed"] else "⚠️"
            lines.append(f"- {status} {item['item']}")

        lines.extend([
            "",
            "## Summary",
            f"- **Addressed:** {data['completed_count']} items",
            f"- **Needs Attention:** {data['total_count'] - data['completed_count']} items",
            "",
            "**Next Steps:**",
            "- Review items marked ⚠️ and address as needed",
            "- Document evidence for each item in control plan",
            "- Update this checklist as mitigations are implemented",
        ])

        content = "\n".join(lines)
        return self.add_header(content)


def generate_ai_risk_checklist(analysis: ProjectAnalysis) -> str:
    """Convenience function to generate AI risk checklist markdown."""
    generator = AIRiskChecklistGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
