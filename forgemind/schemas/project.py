"""Project data models."""

from typing import Optional

from pydantic import BaseModel, Field


class ProjectMetadata(BaseModel):
    """Project identification and classification."""

    name: str = Field(..., description="Project name")
    slug: str = Field(..., description="URL-safe project identifier")
    domain: str = Field(
        default="generic",
        description="Classified domain (ai_project, software_project, qms_iso, etc.)",
    )
    detected_domain: bool = Field(
        default=False, description="True if domain was auto-detected, not explicit"
    )


class ProjectInput(BaseModel):
    """Raw parsed sections from Markdown input."""

    objective: str = Field(
        default="Not evidenced in available input.",
        description="Project objective/goal",
    )
    context: str = Field(
        default="Not evidenced in available input.",
        description="Business/technical context",
    )
    scope: str = Field(
        default="Not evidenced in available input.",
        description="In-scope items",
    )
    out_of_scope: Optional[str] = Field(
        default=None, description="Out-of-scope items"
    )
    constraints: str = Field(
        default="Not evidenced in available input.",
        description="Constraints (timeline, budget, resources, etc.)",
    )
    stakeholders: Optional[str] = Field(default=None, description="Stakeholder list")
    current_state: Optional[str] = Field(default=None, description="Current state")
    desired_state: Optional[str] = Field(default=None, description="Desired end state")
    risks: Optional[str] = Field(default=None, description="Pre-identified risks")
    systems: Optional[str] = Field(
        default=None, description="Systems/tools involved"
    )
    evidence: Optional[str] = Field(
        default=None, description="Available evidence/references"
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")
    success_criteria: Optional[str] = Field(
        default=None, description="Success metrics"
    )
    timeline: Optional[str] = Field(default=None, description="Proposed timeline")

    def has_critical_sections(self) -> bool:
        """Check if critical sections exist (not just defaults)."""
        default = "Not evidenced in available input."
        has_objective = self.objective != default
        has_context = self.context != default
        has_scope = self.scope != default
        return has_objective or has_context or has_scope


class ProjectAnalysis(BaseModel):
    """Complete project analysis result."""

    metadata: ProjectMetadata
    input: ProjectInput
    rdmaicsi_phases: list = Field(default_factory=list, description="RDMAICSI phases")
    senge_disciplines: list = Field(default_factory=list, description="Senge disciplines")
    lean_findings: dict = Field(default_factory=dict, description="Lean analysis")
    six_sigma_tools: dict = Field(default_factory=dict, description="Six Sigma frameworks")
    risks: list = Field(default_factory=list, description="Risk register")
    assumptions: list = Field(default_factory=list, description="Assumption log")
    acceptance_criteria: list = Field(
        default_factory=list, description="Acceptance criteria"
    )
    backlog: list = Field(default_factory=list, description="Prioritized backlog")
    control_plan: list = Field(default_factory=list, description="Control items")
    decision_log: list = Field(default_factory=list, description="Decision log")
    maturity_estimate: str = Field(
        default="Emerging", description="Project maturity estimate"
    )
