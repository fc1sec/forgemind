"""Complete project analysis orchestration."""

from forgemind.core.classifier import classify_domain
from forgemind.core.intake import extract_project_slug, parse_markdown
from forgemind.core.lean import generate_lean_analysis
from forgemind.core.rdmaicsi import generate_rdmaicsi_phases
from forgemind.core.senge import generate_senge_disciplines
from forgemind.core.six_sigma import generate_six_sigma_tools
from forgemind.domains import backlog_generator, risk_generator
from forgemind.schemas.project import (
    ProjectAnalysis,
    ProjectMetadata,
)


def analyze_project(file_path: str) -> ProjectAnalysis:
    """Perform complete project analysis."""

    # Parse input
    project_input = parse_markdown(file_path)
    slug = extract_project_slug(file_path)

    # Classify domain
    domain, is_detected = classify_domain(project_input)

    # Create metadata
    metadata = ProjectMetadata(
        name=slug.replace("-", " ").title(),
        slug=slug,
        domain=domain,
        detected_domain=is_detected,
    )

    # Generate all methodological outputs
    rdmaicsi = [p.model_dump() for p in generate_rdmaicsi_phases()]
    senge = [d.model_dump() for d in generate_senge_disciplines()]
    lean = generate_lean_analysis(project_input)
    six_sigma = generate_six_sigma_tools(project_input)

    # Generate domain-specific analyses
    risks = risk_generator.generate_risks(domain, project_input)
    backlog = backlog_generator.generate_backlog(domain, project_input)
    assumptions = _generate_assumptions(project_input)
    acceptance_criteria = _generate_acceptance_criteria(project_input)
    control_plan = _generate_control_plan(project_input)
    decisions = _generate_decisions(project_input)
    maturity = _estimate_maturity(project_input)

    return ProjectAnalysis(
        metadata=metadata,
        input=project_input,
        rdmaicsi_phases=rdmaicsi,
        senge_disciplines=senge,
        lean_findings=lean.model_dump(),
        six_sigma_tools=six_sigma.model_dump(),
        risks=risks,
        assumptions=assumptions,
        acceptance_criteria=acceptance_criteria,
        backlog=backlog,
        control_plan=control_plan,
        decision_log=decisions,
        maturity_estimate=maturity,
    )


def _generate_assumptions(project_input) -> list[dict]:
    """Generate assumption log from project input."""
    assumptions = []

    if project_input.objective != "Not evidenced in available input.":
        assumptions.append({
            "assumption": f"The objective is: {project_input.objective[:80]}",
            "source": "Project input",
            "risk_if_false": "Work delivers wrong outcome",
            "validation_needed": True,
            "status": "unvalidated",
        })

    if project_input.constraints and project_input.constraints != "Not evidenced in available input.":
        assumptions.append({
            "assumption": "The listed constraints are accurate and complete",
            "source": "Project constraints",
            "risk_if_false": "Discover surprise constraints mid-project",
            "validation_needed": True,
            "status": "unvalidated",
        })

    # Always add core governance assumptions
    assumptions.extend([
        {
            "assumption": "Stakeholders are aligned on success criteria",
            "source": "Method governance",
            "risk_if_false": "Misaligned delivery; rework",
            "validation_needed": True,
            "status": "unvalidated",
        },
        {
            "assumption": "Required decision-makers will be available when needed",
            "source": "Method governance",
            "risk_if_false": "Project blocked waiting for decisions",
            "validation_needed": True,
            "status": "unvalidated",
        },
    ])

    return assumptions


def _generate_acceptance_criteria(project_input) -> list[dict]:
    """Generate acceptance criteria from project input."""
    criteria = []
    counter = 1

    # From explicit success criteria
    if project_input.success_criteria:
        for line in project_input.success_criteria.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                criteria.append({
                    "id": f"AC-{counter:03d}",
                    "criterion": line,
                    "verification_method": "TBD",
                    "evidence_expected": "Measurement or attestation",
                    "owner_placeholder": "[Owner to be assigned]",
                })
                counter += 1

    # Default criteria if none specified
    if not criteria:
        criteria = [
            {
                "id": "AC-001",
                "criterion": "Objective is achieved as defined",
                "verification_method": "Review against objective statement",
                "evidence_expected": "Completed deliverables matching scope",
                "owner_placeholder": "[Owner to be assigned]",
            },
            {
                "id": "AC-002",
                "criterion": "All acceptance criteria met and signed off",
                "verification_method": "Stakeholder review and approval",
                "evidence_expected": "Signed acceptance document",
                "owner_placeholder": "[Owner to be assigned]",
            },
            {
                "id": "AC-003",
                "criterion": "No critical risks remain unmitigated",
                "verification_method": "Risk register review",
                "evidence_expected": "Risk register showing all critical risks mitigated",
                "owner_placeholder": "[Owner to be assigned]",
            },
            {
                "id": "AC-004",
                "criterion": "Control plan is in place and functioning",
                "verification_method": "Control plan audit",
                "evidence_expected": "Control metrics show plan is working",
                "owner_placeholder": "[Owner to be assigned]",
            },
        ]

    return criteria


def _generate_control_plan(project_input) -> list[dict]:
    """Generate control plan."""
    return [
        {
            "control_item": "Stakeholder alignment",
            "method": "Weekly check-in or status update",
            "frequency": "Weekly",
            "owner_placeholder": "[Project Manager]",
            "evidence": "Meeting notes and decision log",
            "reaction_plan_if_failed": "Escalate to sponsor; clarify scope",
        },
        {
            "control_item": "Risk tracking",
            "method": "Review risk register and trigger events",
            "frequency": "Bi-weekly",
            "owner_placeholder": "[Risk Owner]",
            "evidence": "Risk register with status updates",
            "reaction_plan_if_failed": "Activate mitigation plan; escalate if necessary",
        },
        {
            "control_item": "Scope change",
            "method": "Change request review and approval",
            "frequency": "As needed",
            "owner_placeholder": "[Sponsor]",
            "evidence": "Approved change request with impact analysis",
            "reaction_plan_if_failed": "Reject change or extend timeline/budget",
        },
        {
            "control_item": "Acceptance criteria status",
            "method": "Review evidence and test results",
            "frequency": "Bi-weekly or at milestones",
            "owner_placeholder": "[QA Lead]",
            "evidence": "Test report or verification checklist",
            "reaction_plan_if_failed": "Return to development; add to rework list",
        },
    ]


def _generate_decisions(project_input) -> list[dict]:
    """Generate starter decision log."""
    return [
        {
            "id": "D-001",
            "decision": f"Proceed with project focused on: {project_input.objective[:80]}",
            "context": "Project has been recognized and scope has been defined",
            "alternatives_considered": [
                "Defer project to future period",
                "Reduce scope to MVP",
                "Cancel project",
            ],
            "rationale": "Aligns with objectives and has stakeholder support",
            "owner_placeholder": "[Sponsor]",
            "date_placeholder": "[Date to be recorded]",
            "evidence_reference": "Project charter and approval",
        },
        {
            "id": "D-002",
            "decision": "Use ForgeMind MethodOps framework for execution governance",
            "context": "Need structured approach to ensure readiness before agent execution",
            "alternatives_considered": [
                "Ad-hoc execution without structure",
                "Alternative methodology framework",
            ],
            "rationale": "Provides governance gates, assumption tracking, and risk discipline",
            "owner_placeholder": "[Project Manager]",
            "date_placeholder": "[Date to be recorded]",
            "evidence_reference": "Project analysis output",
        },
    ]


def _estimate_maturity(project_input) -> str:
    """Estimate project maturity based on available information."""
    # Score based on how many critical sections are filled out
    default = "Not evidenced in available input."
    filled_sections = sum([
        project_input.objective != default,
        project_input.context != default,
        project_input.scope != default,
        project_input.constraints != default,
        bool(project_input.risks),
        bool(project_input.success_criteria),
        bool(project_input.stakeholders),
    ])

    if filled_sections < 2:
        return "Emerging (early-stage, needs structure)"
    elif filled_sections < 4:
        return "Developing (some clarity, gaps to address)"
    elif filled_sections < 6:
        return "Structured (mostly clear, ready for governance)"
    else:
        return "Ready (well-structured, ready for execution)"
