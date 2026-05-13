"""Risk management models."""

from pydantic import BaseModel, Field


class Risk(BaseModel):
    """Individual risk entry."""

    id: str = Field(..., description="Unique risk identifier")
    risk: str = Field(..., description="Risk statement")
    cause: str = Field(..., description="Root cause")
    impact: str = Field(..., description="Impact description")
    probability: str = Field(
        default="Medium", description="Probability: Low, Medium, High"
    )
    severity: str = Field(
        default="Medium", description="Severity: Low, Medium, High"
    )
    mitigation: str = Field(
        default="To be determined", description="Mitigation strategy"
    )
    owner_placeholder: str = Field(
        default="[Owner to be assigned]", description="Risk owner"
    )
    human_review_required: bool = Field(
        default=False, description="Requires human review"
    )


class RiskRegister(BaseModel):
    """Collection of risks."""

    risks: list[Risk] = Field(default_factory=list, description="Risk items")

    def high_risks(self) -> list[Risk]:
        """Get high-probability or high-severity risks."""
        return [
            r
            for r in self.risks
            if r.probability == "High" or r.severity == "High"
        ]

    def count_by_severity(self) -> dict:
        """Count risks by severity."""
        return {
            "Low": len([r for r in self.risks if r.severity == "Low"]),
            "Medium": len([r for r in self.risks if r.severity == "Medium"]),
            "High": len([r for r in self.risks if r.severity == "High"]),
        }
