from typing import Any, Optional
from pydantic import BaseModel
from app.models.user import User
from app.permissions.checker import Decision

class AgentState(BaseModel):
    task_id: str
    user_message: str
    user: User

    plan: Optional[str] = None
    selected_tool: Optional[str] = None
    tool_input: Optional[dict[str, Any]] = None

    decision: Optional[Decision] = None
    decision_reason: Optional[str] = None

    tool_result: Optional[Any] = None
    tool_error: Optional[str] = None
    retry_count: int = 0

    final_response: Optional[str] = None