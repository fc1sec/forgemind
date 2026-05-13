"""Backlog and work item models."""

from typing import Optional

from pydantic import BaseModel, Field


class BacklogItem(BaseModel):
    """Individual work item."""

    id: str = Field(..., description="Item identifier (e.g., BP-001)")
    epic: str = Field(..., description="Epic/category")
    task: str = Field(..., description="Task description")
    priority: str = Field(
        default="P2", description="Priority: P0, P1, P2, P3"
    )
    impact: str = Field(
        default="Medium", description="Business impact"
    )
    effort: str = Field(
        default="Medium", description="Effort estimate (Small, Medium, Large)"
    )
    dependency: Optional[str] = Field(
        default=None, description="Depends on item ID"
    )
    acceptance_criteria: Optional[list[str]] = Field(
        default=None, description="Acceptance criteria"
    )


class Backlog(BaseModel):
    """Prioritized work backlog."""

    items: list[BacklogItem] = Field(default_factory=list, description="Backlog items")

    def by_priority(self, priority: str) -> list[BacklogItem]:
        """Get items by priority."""
        return [i for i in self.items if i.priority == priority]

    def count_by_priority(self) -> dict:
        """Count items by priority."""
        return {
            "P0": len(self.by_priority("P0")),
            "P1": len(self.by_priority("P1")),
            "P2": len(self.by_priority("P2")),
            "P3": len(self.by_priority("P3")),
        }

    def critical_path(self) -> list[BacklogItem]:
        """Get P0 items (critical path)."""
        return self.by_priority("P0")
