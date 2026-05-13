"""RDMAICSI (8-phase continuous improvement) engine."""

from pydantic import BaseModel


class RDMAICSIPhase(BaseModel):
    """Single RDMAICSI phase."""

    phase: str
    purpose: str
    key_questions: list[str]
    required_evidence: list[str]
    expected_output: str
    risk_if_skipped: str


def generate_rdmaicsi_phases() -> list[RDMAICSIPhase]:
    """Generate all 8 RDMAICSI phases with guidance."""
    return [
        RDMAICSIPhase(
            phase="Recognize",
            purpose="Identify the opportunity or problem that needs addressing",
            key_questions=[
                "What is the current situation?",
                "What problem or opportunity exists?",
                "Who is affected?",
                "What triggers this need now?",
            ],
            required_evidence=[
                "Stakeholder interviews or input",
                "Current state description",
                "Problem statement or opportunity scope",
            ],
            expected_output="Clear problem statement or opportunity definition",
            risk_if_skipped="Solution built for wrong problem; misaligned stakeholders",
        ),
        RDMAICSIPhase(
            phase="Define",
            purpose="Clearly define the scope, objectives, and success criteria",
            key_questions=[
                "What exactly are we solving for?",
                "What is in/out of scope?",
                "Who decides success?",
                "What are hard constraints?",
            ],
            required_evidence=[
                "Objective statement",
                "Scope document",
                "Success criteria or acceptance criteria",
                "Constraint list",
            ],
            expected_output="Project charter with scope, objectives, and criteria",
            risk_if_skipped="Scope creep; unclear exit; rework due to ambiguity",
        ),
        RDMAICSIPhase(
            phase="Measure",
            purpose="Establish baseline metrics and measurement discipline",
            key_questions=[
                "How will we know we succeeded?",
                "What is the baseline?",
                "What metrics matter?",
                "How frequently do we measure?",
            ],
            required_evidence=[
                "Metric definitions",
                "Baseline measurements",
                "Measurement plan (frequency, owner, method)",
            ],
            expected_output="Measurement framework with baseline and targets",
            risk_if_skipped="Cannot verify success; no control over quality",
        ),
        RDMAICSIPhase(
            phase="Analyze",
            purpose="Investigate root causes and understand the current state deeply",
            key_questions=[
                "What are the root causes?",
                "What assumptions are we making?",
                "What could go wrong?",
                "What evidence do we have?",
            ],
            required_evidence=[
                "Root cause analysis (5 Whys, Ishikawa, etc.)",
                "Risk register",
                "Assumption log",
                "Current process/system documentation",
            ],
            expected_output="Root cause analysis, risk register, and assumption log",
            risk_if_skipped="Treating symptoms, not root causes; unmanaged risks",
        ),
        RDMAICSIPhase(
            phase="Improve",
            purpose="Design and implement solutions based on analysis",
            key_questions=[
                "What solutions address root causes?",
                "Have we tested assumptions?",
                "What is our change management plan?",
                "How do we ensure adoption?",
            ],
            required_evidence=[
                "Solution design document",
                "Backlog of improvements",
                "Change management plan",
                "Test plan or pilot results",
            ],
            expected_output="Approved solution design with implementation plan",
            risk_if_skipped="Solutions don't address real problems; poor adoption",
        ),
        RDMAICSIPhase(
            phase="Control",
            purpose="Implement controls to sustain and monitor the improvement",
            key_questions=[
                "How do we prevent backsliding?",
                "What controls are needed?",
                "Who owns ongoing control?",
                "How do we respond if metrics drift?",
            ],
            required_evidence=[
                "Control plan (what, how, who, frequency)",
                "Standard work documentation",
                "SOP or runbook",
                "Monitoring and alert strategy",
            ],
            expected_output="Control plan with standard work and monitoring",
            risk_if_skipped="Improvements fade away; regression to old way",
        ),
        RDMAICSIPhase(
            phase="Standardize",
            purpose="Standardize the new process across the organization",
            key_questions=[
                "How do we scale this across teams?",
                "What training is needed?",
                "How do we communicate standards?",
                "How do we maintain consistency?",
            ],
            required_evidence=[
                "Standard operating procedure",
                "Training materials and completion records",
                "Communication plan and execution",
                "Audit results showing compliance",
            ],
            expected_output="Standardized process documented and deployed",
            risk_if_skipped="Inconsistent execution; loss of gains",
        ),
        RDMAICSIPhase(
            phase="Integrate",
            purpose="Embed the improvement into systems, culture, and strategy",
            key_questions=[
                "Is this part of our standard way of working?",
                "How does this connect to other processes?",
                "What systems support this?",
                "Is there cultural adoption?",
            ],
            required_evidence=[
                "Integration with other processes documented",
                "System changes or tool updates completed",
                "Cultural indicators (team feedback, metrics sustainment)",
                "Long-term sustainability plan",
            ],
            expected_output="Sustained improvement integrated into operations",
            risk_if_skipped="Improvement is temporary; no lasting change",
        ),
    ]
