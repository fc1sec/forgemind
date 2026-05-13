"""Lean thinking analysis for project execution."""

from pydantic import BaseModel


class LeanAnalysis(BaseModel):
    """Lean waste and flow findings."""

    waste_scan: dict
    flow_risks: list[str]
    standard_work_opportunities: list[str]
    rework_risks: list[str]
    handoff_risks: list[str]


def generate_lean_analysis(project_input) -> LeanAnalysis:
    """Identify Lean waste categories and flow risks in project."""

    waste_scan = {
        "overproduction": [
            "Generating outputs nobody asked for or needs yet",
            "Over-documenting or over-specifying",
        ],
        "waiting": [
            "Delays waiting for decisions or approvals",
            "Dependencies on other teams or systems",
            "Unclear stakeholder availability",
        ],
        "overprocessing": [
            "Excessive review cycles or approvals",
            "Redundant handoffs between teams",
            "Unclear or inconsistent process",
        ],
        "defects": [
            "Rework due to ambiguous requirements",
            "Misunderstood acceptance criteria",
            "Incomplete testing",
        ],
        "motion/searching": [
            "Difficulty finding information",
            "Unclear communication channels",
            "Information scattered across tools",
        ],
        "inventory/backlog": [
            "Unreviewed items in backlog",
            "Work sitting in progress",
            "Decisions not made causing blockage",
        ],
        "handoff_loss": [
            "Knowledge loss between handoffs",
            "Unclear ownership or responsibility",
            "Poor documentation at boundaries",
        ],
        "unused_knowledge": [
            "Past lessons not applied",
            "Expert knowledge not leveraged",
            "Historical data not used",
        ],
    }

    flow_risks = [
        "Unclear decision-making authority (causes waiting)",
        "Ambiguous acceptance criteria (causes rework)",
        "Missing or unclear dependencies (causes surprises)",
        "Synchronous approval processes (causes waiting)",
        "Siloed information (causes motion/searching)",
    ]

    standard_work_opportunities = [
        "Define standard templates for decisions",
        "Create clear acceptance criteria checklist",
        "Document dependency map upfront",
        "Define asynchronous approval process",
        "Create information hub or single source of truth",
    ]

    rework_risks = [
        "Requirements not fully understood",
        "Acceptance criteria not testable",
        "Incomplete stakeholder alignment",
        "Scope changes mid-project",
        "Insufficient testing or validation",
    ]

    handoff_risks = [
        "Knowledge not documented at handoff",
        "Ownership unclear after transition",
        "No acceptance gate at handoff boundary",
        "Recipient not prepared to receive work",
        "No rollback plan if handoff fails",
    ]

    return LeanAnalysis(
        waste_scan=waste_scan,
        flow_risks=flow_risks,
        standard_work_opportunities=standard_work_opportunities,
        rework_risks=rework_risks,
        handoff_risks=handoff_risks,
    )
