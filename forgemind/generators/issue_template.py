"""Generate GitHub issue templates for feedback on agent-generated code."""

from forgemind.generators.base import BaseGenerator
from forgemind.schemas.project import ProjectAnalysis


class IssueTemplateGenerator(BaseGenerator):
    """Generate issue templates for bug/feedback reporting."""

    def generate(self, analysis: ProjectAnalysis) -> dict:
        """Generate issue template data."""
        template = {
            "project": analysis.metadata.name,
            "version": "1.1",
            "domain": analysis.metadata.domain,
        }
        return template

    def _format_markdown_impl(self, data: dict) -> str:
        """Format as GitHub-compatible issue template."""
        lines = [
            "## Issue Type",
            "- [ ] Bug Report",
            "- [ ] Feature Request",
            "- [ ] Question",
            "",
            "## Description",
            "Describe the issue or feedback here.",
            "",
            "## Steps to Reproduce (if bug)",
            "1. ",
            "2. ",
            "3. ",
            "",
            "## Expected Behavior",
            "What should happen?",
            "",
            "## Actual Behavior",
            "What actually happened?",
            "",
            "## Environment",
            f"- **ForgeMind Version:** {data['version']}",
            f"- **Project Domain:** {data['domain']}",
            "- **Agent Used:** [Claude Code / Codex / Other]",
            "- **OS:** ",
            "- **Python Version:** ",
            "",
            "## Screenshots or Code Samples",
            "```python",
            "# Paste relevant code here",
            "```",
            "",
            "## Related Issues",
            "Closes #[issue number] (if applicable)",
        ]

        content = "\n".join(lines)
        return self.add_header(content)


def generate_issue_template(analysis: ProjectAnalysis) -> str:
    """Convenience function to generate issue template."""
    generator = IssueTemplateGenerator()
    data = generator.generate(analysis)
    return generator.format_markdown(data)
