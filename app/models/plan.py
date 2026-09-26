from typing import Any
from pydantic import BaseModel, Field

class PlanOutput(BaseModel):
    tool: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    reasoning: str