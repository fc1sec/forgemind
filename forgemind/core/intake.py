"""Markdown project file parser."""

from pathlib import Path
from typing import Optional

from forgemind.schemas.project import ProjectInput


def parse_markdown(file_path: str) -> ProjectInput:
    """Parse Markdown project file and extract sections.

    Handles missing sections gracefully with defaults.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {file_path}")

    content = path.read_text(encoding="utf-8")
    sections = _extract_sections(content)

    return ProjectInput(
        objective=sections.get("Objective", "Not evidenced in available input."),
        context=sections.get("Context", "Not evidenced in available input."),
        scope=sections.get("Scope", "Not evidenced in available input."),
        out_of_scope=sections.get("Out of Scope"),
        constraints=sections.get("Constraints", "Not evidenced in available input."),
        stakeholders=sections.get("Stakeholders"),
        current_state=sections.get("Current State"),
        desired_state=sections.get("Desired State"),
        risks=sections.get("Risks"),
        systems=sections.get("Systems"),
        evidence=sections.get("Evidence"),
        notes=sections.get("Notes"),
        success_criteria=sections.get("Success Criteria"),
        timeline=sections.get("Timeline"),
    )


def _extract_sections(content: str) -> dict[str, str]:
    """Extract all H2 and H3 sections from Markdown.

    Returns a dict mapping section names to their content.
    """
    sections = {}
    current_section: Optional[str] = None
    current_content: list[str] = []

    for line in content.split("\n"):
        # Check for H2 or H3 headers
        if line.startswith("## "):
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        elif line.startswith("### "):
            # Treat H3 as part of current section
            if current_section:
                current_content.append(line)
        elif line.startswith("# "):
            # H1 is project title, skip
            continue
        else:
            # Regular content
            if current_section:
                current_content.append(line)

    # Save final section
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def extract_project_slug(file_path: str) -> str:
    """Generate a URL-safe project slug from file name or content."""
    path = Path(file_path)
    name = path.stem  # filename without extension

    # Convert to URL-safe slug
    slug = (
        name.lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace(".", "-")
    )
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = slug.strip("-")

    return slug or "project"
