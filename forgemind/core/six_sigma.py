"""Six Sigma problem-solving frameworks."""

from pydantic import BaseModel


class SixSigmaTools(BaseModel):
    """Six Sigma frameworks and questions."""

    five_whys_framework: dict
    ishikawa_categories: dict
    fmea_starter: dict
    measurement_questions: list[str]
    control_questions: list[str]


def generate_six_sigma_tools(project_input) -> SixSigmaTools:
    """Generate Six Sigma starter frameworks."""

    five_whys = {
        "structure": "Ask 'Why?' after each answer until root cause emerges",
        "level_1": f"Why is this a problem? {project_input.objective}",
        "level_2": "Why does that cause a problem?",
        "level_3": "Why does that underlying issue exist?",
        "level_4": "Why hasn't this been fixed before?",
        "level_5": "What is the deepest root cause?",
        "note": "Usually root cause appears by level 3-5",
    }

    ishikawa = {
        "purpose": "Organize potential causes into categories",
        "people": [
            "Skills or knowledge gaps",
            "Unclear roles or ownership",
            "Insufficient team size",
            "Lack of training",
        ],
        "method": [
            "Unclear process or standards",
            "Inadequate procedures",
            "Process not documented",
            "Process not followed",
        ],
        "data": [
            "Insufficient information",
            "Inaccurate data",
            "Data not accessible",
            "Assumptions not tested",
        ],
        "technology": [
            "Tool limitations",
            "Integration gaps",
            "Outdated systems",
            "Technical knowledge gaps",
        ],
        "measurement": [
            "Metrics not defined",
            "Measurement method unclear",
            "No baseline",
            "Frequency inadequate",
        ],
        "governance": [
            "Unclear decision authority",
            "Policy gaps",
            "Compliance not enforced",
            "Approval process broken",
        ],
        "environment": [
            "Time constraints",
            "Resource constraints",
            "Organizational change",
            "External dependencies",
        ],
        "customer": [
            "Unclear requirements",
            "Changing priorities",
            "Conflicting needs",
            "Acceptance unclear",
        ],
    }

    fmea = {
        "structure": "Identify potential failures, likelihood, impact, and controls",
        "columns": [
            "Potential Failure Mode",
            "Potential Cause",
            "Potential Effect",
            "Severity (1-10)",
            "Occurrence (1-10)",
            "Detection (1-10)",
            "RPN (S×O×D)",
            "Recommended Control",
        ],
        "focus_on_high_rpn": "Items with RPN > 100 need mitigation",
        "note": "Start with top 5-10 risks, expand if time allows",
    }

    measurement_questions = [
        "How do we define success in measurable terms?",
        "What baseline metrics exist today?",
        "What targets are we trying to hit?",
        "How frequently should we measure?",
        "Who is accountable for measurement?",
        "Where do we get accurate data?",
        "Are metrics leading or lagging indicators?",
        "How will we detect if something is drifting off track?",
    ]

    control_questions = [
        "What could cause us to backslide from this improvement?",
        "What controls prevent that regression?",
        "Who is responsible for each control?",
        "How frequently do we check that controls are working?",
        "What is our reaction plan if a control fails?",
        "How will we know if the control is effective?",
        "What documentation supports this control?",
        "How is this control standardized across teams?",
    ]

    return SixSigmaTools(
        five_whys_framework=five_whys,
        ishikawa_categories=ishikawa,
        fmea_starter=fmea,
        measurement_questions=measurement_questions,
        control_questions=control_questions,
    )
