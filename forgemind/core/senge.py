"""Peter Senge's Five Disciplines of Learning Organizations."""

from pydantic import BaseModel


class SengeDiscipline(BaseModel):
    """Single Senge discipline."""

    discipline: str
    purpose: str
    diagnostic_questions: list[str]
    project_risk_if_ignored: str
    recommended_practice: str


def generate_senge_disciplines() -> list[SengeDiscipline]:
    """Generate all 5 Senge disciplines."""
    return [
        SengeDiscipline(
            discipline="Systems Thinking",
            purpose="See the whole system, not just parts; understand feedback loops and consequences",
            diagnostic_questions=[
                "Do we understand how this project affects other parts of the organization?",
                "Are we seeing side effects or unintended consequences?",
                "Do we understand the feedback loops (how changes cause reactions)?",
                "Are we addressing symptoms or root causes?",
            ],
            project_risk_if_ignored="Unintended consequences; solutions that break other systems",
            recommended_practice="Map dependencies, stakeholders, and system interactions before deciding",
        ),
        SengeDiscipline(
            discipline="Mental Models",
            purpose="Make explicit the assumptions and beliefs that drive decisions",
            diagnostic_questions=[
                "What assumptions are we making without evidence?",
                "Are our mental models aligned across the team?",
                "What beliefs might be limiting our solutions?",
                "Have we questioned conventional wisdom?",
            ],
            project_risk_if_ignored="Hidden disagreement; wrong assumptions drive poor solutions",
            recommended_practice="Document assumptions explicitly; test them; surface disagreement early",
        ),
        SengeDiscipline(
            discipline="Shared Vision",
            purpose="Align the team around a common future state they genuinely want to create",
            diagnostic_questions=[
                "Do all stakeholders share a common vision of success?",
                "Is the vision inspiring or just a checklist?",
                "Are people building toward this or just following orders?",
                "How connected is this project to the broader purpose?",
            ],
            project_risk_if_ignored="Misaligned effort; low engagement; divergent priorities mid-project",
            recommended_practice="Co-create vision; connect to broader purpose; revisit regularly",
        ),
        SengeDiscipline(
            discipline="Personal Mastery",
            purpose="Build individual capability, commitment, and accountability",
            diagnostic_questions=[
                "Do team members have the skills needed for this work?",
                "Is there genuine commitment or just compliance?",
                "Are people learning and growing through this project?",
                "Are there skill or knowledge gaps?",
            ],
            project_risk_if_ignored="Low-quality work; people grinding without growth; burnout",
            recommended_practice="Invest in skill development; create psychological safety; match roles to growth",
        ),
        SengeDiscipline(
            discipline="Team Learning",
            purpose="Enable the team to learn together and adapt as understanding grows",
            diagnostic_questions=[
                "How does the team reflect on progress and adjust?",
                "Are we learning from early mistakes?",
                "Is information shared transparently?",
                "Are there mechanisms for collective problem-solving?",
            ],
            project_risk_if_ignored="Repeating mistakes; siloed knowledge; inability to adapt",
            recommended_practice="Regular retrospectives, knowledge sharing sessions, and collaborative problem-solving",
        ),
    ]
