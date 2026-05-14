"""Domain-specific risk generation."""

from __future__ import annotations


def generate_risks(domain: str, project_input) -> list[dict]:
    """Generate domain-specific risks."""

    base_risks = [
        {
            "id": "R-001",
            "risk": "Ambiguous acceptance criteria lead to rework",
            "cause": "Acceptance criteria not clearly defined or testable",
            "impact": "Rework, schedule slip, cost overrun",
            "probability": "Medium",
            "severity": "Medium",
            "mitigation": "Define specific, testable acceptance criteria upfront",
            "owner_placeholder": "[Owner to be assigned]",
            "human_review_required": True,
        },
        {
            "id": "R-002",
            "risk": "Stakeholder misalignment causes scope creep",
            "cause": "Stakeholders have different visions of success",
            "impact": "Scope creep, timeline extension, budget overrun",
            "probability": "Medium",
            "severity": "High",
            "mitigation": "Document shared vision; align stakeholders early; control changes",
            "owner_placeholder": "[Sponsor]",
            "human_review_required": True,
        },
        {
            "id": "R-003",
            "risk": "Critical assumptions not validated",
            "cause": "Assumptions made without evidence",
            "impact": "Solution doesn't work; needs rework",
            "probability": "Medium",
            "severity": "High",
            "mitigation": "Identify assumptions; validate or test before full execution",
            "owner_placeholder": "[Owner to be assigned]",
            "human_review_required": True,
        },
    ]

    # Domain-specific risks
    if domain == "ai_project":
        base_risks.extend([
            {
                "id": "R-101",
                "risk": "AI agent operates outside intended boundaries",
                "cause": "Autonomy boundaries not clearly defined",
                "impact": "Uncontrolled agent actions; unexpected results",
                "probability": "High",
                "severity": "High",
                "mitigation": "Define explicit execution boundaries; human review gates",
                "owner_placeholder": "[AI Safety Lead]",
                "human_review_required": True,
            },
            {
                "id": "R-102",
                "risk": "Insufficient evidence to support agent decision-making",
                "cause": "Input data missing, unclear, or insufficient",
                "impact": "Agent makes poor decisions; rework or harm",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Audit data quality; define minimum evidence thresholds",
                "owner_placeholder": "[Data Lead]",
                "human_review_required": True,
            },
            {
                "id": "R-103",
                "risk": "Agent execution scope too broad for safety",
                "cause": "Scope not constrained; too much autonomy granted",
                "impact": "Unintended consequences; hard to roll back",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Start with narrow scope; MVP approach; progressive expansion",
                "owner_placeholder": "[Sponsor]",
                "human_review_required": True,
            },
        ])

    elif domain == "software_project":
        base_risks.extend([
            {
                "id": "R-201",
                "risk": "Missing test coverage causes production defects",
                "cause": "Insufficient testing or test gaps",
                "impact": "Defects in production; customer impact",
                "probability": "High",
                "severity": "High",
                "mitigation": "Define test strategy upfront; require coverage metrics",
                "owner_placeholder": "[QA Lead]",
                "human_review_required": False,
            },
            {
                "id": "R-202",
                "risk": "Unclear rollback plan if deployment fails",
                "cause": "No rollback procedure defined",
                "impact": "Extended outage; customer impact",
                "probability": "Low",
                "severity": "High",
                "mitigation": "Define rollback procedure; test it before deployment",
                "owner_placeholder": "[DevOps Lead]",
                "human_review_required": True,
            },
            {
                "id": "R-203",
                "risk": "Regression in other features",
                "cause": "Insufficient integration testing; architecture drift",
                "impact": "Broken features; customer complaints",
                "probability": "Medium",
                "severity": "Medium",
                "mitigation": "Full regression testing; architecture review",
                "owner_placeholder": "[QA Lead]",
                "human_review_required": False,
            },
        ])

    elif domain == "qms_iso":
        base_risks.extend([
            {
                "id": "R-301",
                "risk": "Process not documented or controlled",
                "cause": "Documentation gaps; lack of control mechanism",
                "impact": "Audit findings; non-compliance; rework",
                "probability": "High",
                "severity": "High",
                "mitigation": "Document all processes; define control plan",
                "owner_placeholder": "[QMS Lead]",
                "human_review_required": True,
            },
            {
                "id": "R-302",
                "risk": "Evidence gaps for audit",
                "cause": "Work done but not recorded; inadequate records",
                "impact": "Audit non-conformity; questions on effectiveness",
                "probability": "Medium",
                "severity": "Medium",
                "mitigation": "Define evidence requirements upfront; audit as you go",
                "owner_placeholder": "[Auditor]",
                "human_review_required": True,
            },
            {
                "id": "R-303",
                "risk": "Uncontrolled changes to documents or processes",
                "cause": "Document control not enforced",
                "impact": "Version confusion; inconsistency",
                "probability": "Medium",
                "severity": "Medium",
                "mitigation": "Implement document control; approve changes formally",
                "owner_placeholder": "[Document Controller]",
                "human_review_required": True,
            },
        ])

    elif domain == "operations":
        base_risks.extend([
            {
                "id": "R-401",
                "risk": "Workflow handoff breaks down",
                "cause": "Unclear roles, ownership, or handoff criteria",
                "impact": "Work stalls; customer impact; rework",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Define roles, ownership, and acceptance criteria at handoff",
                "owner_placeholder": "[Process Owner]",
                "human_review_required": True,
            },
            {
                "id": "R-402",
                "risk": "Metrics not achieved",
                "cause": "Unclear targets; execution issues",
                "impact": "Operations failure; SLA breaches",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Define targets and controls; monitor closely",
                "owner_placeholder": "[Operations Lead]",
                "human_review_required": False,
            },
        ])

    elif domain == "odoo_erp":
        base_risks.extend([
            {
                "id": "R-501",
                "risk": "Data integrity lost in ERP transition",
                "cause": "Migration issues; configuration gaps",
                "impact": "Incorrect inventory; accounting issues",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Data validation plan; reconciliation before cutover",
                "owner_placeholder": "[Data Steward]",
                "human_review_required": True,
            },
            {
                "id": "R-502",
                "risk": "Lot/serial traceability not configured",
                "cause": "Requirements not understood; implementation gaps",
                "impact": "Cannot track product; regulatory issues",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Clarify traceability requirements; test thoroughly",
                "owner_placeholder": "[ERP Lead]",
                "human_review_required": True,
            },
        ])

    elif domain == "tenders":
        base_risks.extend([
            {
                "id": "R-601",
                "risk": "Technical requirements not fully understood",
                "cause": "RFI/RFQ not sufficiently detailed",
                "impact": "Bid doesn't meet requirements; rejection",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Attend RFI sessions; document all clarifications",
                "owner_placeholder": "[Bid Lead]",
                "human_review_required": True,
            },
            {
                "id": "R-602",
                "risk": "Compliance matrix incomplete or inaccurate",
                "cause": "Compliance requirements not mapped",
                "impact": "Bid rejected for non-compliance",
                "probability": "Medium",
                "severity": "High",
                "mitigation": "Detailed compliance matrix; review with legal/QMS",
                "owner_placeholder": "[Compliance Lead]",
                "human_review_required": True,
            },
        ])

    return base_risks
