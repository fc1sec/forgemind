"""Agent handoff models."""


from pydantic import BaseModel, Field


class HandoffContent(BaseModel):
    """Agent-ready handoff information."""

    objective: str = Field(..., description="Clear objective for agent")
    context: str = Field(..., description="Business and technical context")
    domain: str = Field(..., description="Project domain")
    constraints: list[str] = Field(
        default_factory=list, description="Execution constraints"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Key assumptions"
    )
    risks: list[dict] = Field(default_factory=list, description="Top risks")
    acceptance_criteria: list[str] = Field(
        default_factory=list, description="Acceptance criteria"
    )
    suggested_files: list[str] = Field(
        default_factory=list, description="Files to review"
    )
    do_not_modify: list[str] = Field(
        default_factory=list, description="Areas not to touch"
    )
    testing_expectations: str = Field(
        default="TBD", description="Testing requirements"
    )
    rollback_notes: str = Field(
        default="TBD", description="How to rollback if needed"
    )
    human_review_gates: list[str] = Field(
        default_factory=list, description="Where humans must review"
    )
    definition_of_done: list[str] = Field(
        default_factory=list, description="Completion criteria"
    )
    target_agent: str = Field(
        default="generic-agent",
        description="Target: codex, claude-code, generic-agent",
    )


class Assumption(BaseModel):
    """Individual assumption."""

    assumption: str = Field(..., description="The assumption")
    source: str = Field(..., description="Where this came from")
    risk_if_false: str = Field(..., description="Impact if assumption is wrong")
    validation_needed: bool = Field(
        default=True, description="Does this need validation?"
    )
    status: str = Field(
        default="unvalidated",
        description="Status: unvalidated, partially_validated, validated",
    )


class AcceptanceCriterion(BaseModel):
    """Individual acceptance criterion."""

    id: str = Field(..., description="Criterion ID")
    criterion: str = Field(..., description="What must be true")
    verification_method: str = Field(..., description="How to verify")
    evidence_expected: str = Field(..., description="What evidence proves this")
    owner_placeholder: str = Field(
        default="[Owner to be assigned]", description="Criterion owner"
    )
