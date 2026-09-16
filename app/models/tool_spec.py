from enum import Enum
from typing import Type
from pydantic import BaseModel
from app.models.user import Role

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ToolSpec(BaseModel):
    """Describes a tool the agent is allowed to use."""

    name: str
    description: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    allowed_roles: list[Role]
    rate_limit: int
    risk_level: RiskLevel

    model_config = {"arbitrary_types_allowed": True}

    @property
    def requires_confirmation(self) -> bool:
        return self.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH)

    @property
    def requires_approval(self) -> bool:
        return self.risk_level is RiskLevel.HIGH