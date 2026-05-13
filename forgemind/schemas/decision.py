"""Decision log models."""

from typing import Optional

from pydantic import BaseModel, Field


class Decision(BaseModel):
    """Individual decision entry."""

    id: str = Field(..., description="Decision identifier")
    decision: str = Field(..., description="What was decided")
    context: str = Field(..., description="Why this decision was needed")
    alternatives_considered: list[str] = Field(
        default_factory=list, description="Alternatives evaluated"
    )
    rationale: str = Field(..., description="Why this alternative was chosen")
    owner_placeholder: str = Field(
        default="[Owner to be assigned]", description="Decision maker"
    )
    date_placeholder: str = Field(
        default="[Date to be recorded]", description="Decision date"
    )
    evidence_reference: Optional[str] = Field(
        default=None, description="Reference to supporting evidence"
    )


class DecisionLog(BaseModel):
    """Collection of decisions."""

    decisions: list[Decision] = Field(default_factory=list, description="Decision items")
