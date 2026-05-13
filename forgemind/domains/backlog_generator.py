"""Domain-specific backlog generation."""


def generate_backlog(domain: str, project_input) -> list[dict]:
    """Generate prioritized backlog items."""

    # Core readiness backlog (all projects)
    backlog = [
        {
            "id": "BP-001",
            "epic": "Readiness",
            "task": "Define and document acceptance criteria",
            "priority": "P0",
            "impact": "High",
            "effort": "Medium",
            "dependency": None,
            "acceptance_criteria": [
                "Criteria are testable and measurable",
                "Criteria are accepted by stakeholders",
            ],
        },
        {
            "id": "BP-002",
            "epic": "Readiness",
            "task": "Complete risk register and mitigation plan",
            "priority": "P0",
            "impact": "High",
            "effort": "Medium",
            "dependency": None,
            "acceptance_criteria": [
                "All identified risks have mitigation plan",
                "Risk owners assigned",
            ],
        },
        {
            "id": "BP-003",
            "epic": "Readiness",
            "task": "Validate key assumptions",
            "priority": "P0",
            "impact": "High",
            "effort": "Large",
            "dependency": None,
            "acceptance_criteria": [
                "Critical assumptions tested or evidenced",
                "List of unvalidated assumptions documented",
            ],
        },
        {
            "id": "BP-004",
            "epic": "Readiness",
            "task": "Define control plan and monitoring",
            "priority": "P1",
            "impact": "High",
            "effort": "Medium",
            "dependency": "BP-002",
            "acceptance_criteria": [
                "Controls defined for each critical item",
                "Monitoring frequency and owner assigned",
            ],
        },
        {
            "id": "BP-005",
            "epic": "Governance",
            "task": "Establish human review gates",
            "priority": "P0",
            "impact": "High",
            "effort": "Small",
            "dependency": None,
            "acceptance_criteria": [
                "Review gates clearly defined",
                "Reviewers identified and available",
            ],
        },
    ]

    # Domain-specific backlog
    if domain == "ai_project":
        backlog.extend([
            {
                "id": "BP-101",
                "epic": "AI Safety",
                "task": "Define agent autonomy boundaries and constraints",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": None,
                "acceptance_criteria": [
                    "Boundaries are explicit and testable",
                    "Constraints prevent out-of-scope execution",
                ],
            },
            {
                "id": "BP-102",
                "epic": "AI Safety",
                "task": "Create agent execution test harness",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": "BP-101",
                "acceptance_criteria": [
                    "Harness validates boundary constraints",
                    "Tests cover normal and edge cases",
                ],
            },
            {
                "id": "BP-103",
                "epic": "AI Safety",
                "task": "Define handoff format and protocol",
                "priority": "P1",
                "impact": "Medium",
                "effort": "Medium",
                "dependency": None,
                "acceptance_criteria": [
                    "Agent can consume handoff format",
                    "All critical context included",
                ],
            },
        ])

    elif domain == "software_project":
        backlog.extend([
            {
                "id": "BP-201",
                "epic": "Quality",
                "task": "Define test strategy and coverage requirements",
                "priority": "P0",
                "impact": "High",
                "effort": "Medium",
                "dependency": None,
                "acceptance_criteria": [
                    "Test plan covers normal and edge cases",
                    "Coverage targets defined and agreed",
                ],
            },
            {
                "id": "BP-202",
                "epic": "Deployment",
                "task": "Create deployment plan with rollback procedure",
                "priority": "P1",
                "impact": "High",
                "effort": "Large",
                "dependency": None,
                "acceptance_criteria": [
                    "Rollback procedure tested",
                    "Deployment checklist complete",
                ],
            },
            {
                "id": "BP-203",
                "epic": "Architecture",
                "task": "Review for architectural alignment",
                "priority": "P1",
                "impact": "Medium",
                "effort": "Medium",
                "dependency": None,
                "acceptance_criteria": [
                    "Architecture review completed",
                    "No drift from approved design",
                ],
            },
        ])

    elif domain == "qms_iso":
        backlog.extend([
            {
                "id": "BP-301",
                "epic": "Documentation",
                "task": "Document process in detail",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": None,
                "acceptance_criteria": [
                    "Process documented and approved",
                    "Roles and responsibilities clear",
                ],
            },
            {
                "id": "BP-302",
                "epic": "Control",
                "task": "Establish document control and change process",
                "priority": "P0",
                "impact": "High",
                "effort": "Medium",
                "dependency": "BP-301",
                "acceptance_criteria": [
                    "Document management system in place",
                    "Version control enforced",
                ],
            },
            {
                "id": "BP-303",
                "epic": "Audit Ready",
                "task": "Gather and organize evidence",
                "priority": "P1",
                "impact": "High",
                "effort": "Large",
                "dependency": "BP-301",
                "acceptance_criteria": [
                    "All required evidence collected",
                    "Evidence linked to requirements",
                ],
            },
        ])

    elif domain == "operations":
        backlog.extend([
            {
                "id": "BP-401",
                "epic": "Process",
                "task": "Map workflow and define handoff points",
                "priority": "P0",
                "impact": "High",
                "effort": "Medium",
                "dependency": None,
                "acceptance_criteria": [
                    "Workflow visually mapped",
                    "Handoff criteria defined",
                ],
            },
            {
                "id": "BP-402",
                "epic": "Metrics",
                "task": "Define SLAs and monitoring",
                "priority": "P1",
                "impact": "High",
                "effort": "Medium",
                "dependency": "BP-401",
                "acceptance_criteria": [
                    "SLAs defined and agreed",
                    "Monitoring dashboard created",
                ],
            },
        ])

    elif domain == "odoo_erp":
        backlog.extend([
            {
                "id": "BP-501",
                "epic": "Configuration",
                "task": "Configure lot/serial tracking",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": None,
                "acceptance_criteria": [
                    "Lot/serial fields configured",
                    "Traceability working end-to-end",
                ],
            },
            {
                "id": "BP-502",
                "epic": "Data",
                "task": "Data migration and reconciliation",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": None,
                "acceptance_criteria": [
                    "Data migrated and validated",
                    "Reconciliation completed",
                ],
            },
        ])

    elif domain == "tenders":
        backlog.extend([
            {
                "id": "BP-601",
                "epic": "Compliance",
                "task": "Create detailed compliance matrix",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": None,
                "acceptance_criteria": [
                    "All requirements mapped",
                    "Compliance path clear for each item",
                ],
            },
            {
                "id": "BP-602",
                "epic": "Evidence",
                "task": "Gather technical and compliance evidence",
                "priority": "P0",
                "impact": "High",
                "effort": "Large",
                "dependency": "BP-601",
                "acceptance_criteria": [
                    "All required evidence collected",
                    "Evidence referenced in bid response",
                ],
            },
        ])

    return backlog
