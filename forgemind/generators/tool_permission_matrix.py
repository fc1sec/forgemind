"""Generate tool permission matrices for agent execution constraints."""

from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


class ToolPermissionMatrixGenerator(BaseGenerator):
    """Generate tool permission matrices by domain."""

    # Domain-specific tool policies
    DOMAIN_POLICIES = {
        "ai_project": {
            "Read files": ("✅ Allowed", "Safe introspection of codebase", False),
            "Modify code": ("✅ Conditional", "Only in /generated/ directory", True),
            "External API calls": ("❌ Denied", "Security + API policy", False),
            "Database writes": ("❌ Denied", "Data integrity risk", False),
            "Shell execution": ("✅ Conditional", "Read-only commands only", True),
            "Create pull requests": ("✅ Conditional", "Requires approval gate", True),
            "Delete operations": ("❌ Denied", "Irreversible action", False),
        },
        "software_project": {
            "Read files": ("✅ Allowed", "Code review", False),
            "Modify code": ("✅ Conditional", "Requires test + linter pass", True),
            "Run tests": ("✅ Allowed", "Validation", False),
            "Database migrations": ("⚠️ Restricted", "Requires schema review", True),
            "Deploy to staging": ("✅ Conditional", "CI/CD pipeline only", True),
            "Deploy to production": ("❌ Denied", "Manual approval required", False),
            "Modify secrets": ("❌ Denied", "Credential management risk", False),
        },
        "qms_iso": {
            "Create documents": ("✅ Allowed", "ISO-formatted output", False),
            "Modify procedures": ("⚠️ Restricted", "Document control required", True),
            "Approve procedures": ("❌ Denied", "Management sign-off only", False),
            "Archive records": ("✅ Conditional", "Retention policy", True),
            "Delete records": ("❌ Denied", "Audit trail immutability", False),
            "Sign audit reports": ("❌ Denied", "Authorized person only", False),
        },
        "generic": {
            "Read input": ("✅ Allowed", "Safe", False),
            "Modify output": ("✅ Conditional", "Requires approval", True),
            "External calls": ("⚠️ Restricted", "Policy-dependent", True),
            "Delete operations": ("❌ Denied", "Irreversible", False),
        },
    }

    def generate(self, analysis: ProjectAnalysis) -> dict:
        """Generate tool permission matrix for domain."""
        domain = analysis.metadata.domain
        policies = self.DOMAIN_POLICIES.get(domain, self.DOMAIN_POLICIES["generic"])

        matrix = {
            "domain": domain,
            "project": analysis.metadata.name,
            "tools": [
                {
                    "tool": tool,
                    "permission": permission[0],
                    "reason": permission[1],
                    "requires_review": permission[2],
                }
                for tool, permission in policies.items()
            ],
        }

        return matrix

    def _format_markdown_impl(self, data: dict) -> str:
        """Format matrix as Markdown table."""
        lines = [
            f"# {data['project']} — Tool Permission Matrix",
            f"Domain: {data['domain'].replace('_', ' ').title()}",
            "",
            "## Execution Constraints",
            "",
            "| Tool/Operation | Permission | Reason | Human Review Gate |",
            "|---|---|---|---|",
        ]

        for item in data["tools"]:
            review = "✓ Yes" if item["requires_review"] else "No"
            lines.append(
                f"| {item['tool']} | {item['permission']} | {item['reason']} | {review} |"
            )

        lines.extend([
            "",
            "## Legend",
            "- **✅ Allowed:** Operation permitted without restrictions",
            "- **✅ Conditional:** Operation permitted with approval gate",
            "- **⚠️ Restricted:** Operation allowed with specific conditions",
            "- **❌ Denied:** Operation not permitted",
            "",
            "## Implementation",
            "- Enable only permitted operations in agent environment",
            "- Log all conditional operations for audit",
            "- Implement approval gates before conditional operations",
            "- Review this matrix periodically (quarterly recommended)",
        ])

        content = "\n".join(lines)
        return self.add_header(content)


def generate_tool_permission_matrix(analysis: ProjectAnalysis) -> str:
    """Convenience function to generate tool permission matrix."""
    generator = ToolPermissionMatrixGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
