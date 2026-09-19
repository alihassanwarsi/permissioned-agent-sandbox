from enum import Enum
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.tool_spec import RiskLevel

class ApprovalOutcome(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    REPLAN = "replan"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"

class ApprovalRequest(BaseModel):
    request_id: str
    thread_id: str

    tool_name: str
    tool_input: dict[str, Any]
    risk_level: RiskLevel
    reasoning: str

    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    outcome: Optional[ApprovalOutcome] = None
    decided_by: Optional[str] = None
    note: Optional[str] = None
    modified_input: Optional[dict[str, Any]] = None
    resolved_at: Optional[datetime] = None