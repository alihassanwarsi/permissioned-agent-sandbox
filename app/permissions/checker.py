from enum import Enum
from pydantic import BaseModel
from app.models.tool_spec import ToolSpec
from app.models.user import User
from app.permissions.rate_limiter import RateLimiter

class Decision(str, Enum):
    DENIED = "denied"
    RATE_LIMITED = "rate_limited"
    ALLOWED = "allowed"
    NEEDS_CONFIRMATION = "needs_confirmation"
    NEEDS_APPROVAL = "needs_approval"

class PermissionResult(BaseModel):
    decision: Decision
    reason: str

def check_permission(user: User, tool: ToolSpec, rate_limiter: RateLimiter) -> PermissionResult:
    if user.role not in tool.allowed_roles:
        return PermissionResult(
            decision=Decision.DENIED,
            reason=f"{user.role.value} is not allowed to use '{tool.name}'"
        )

    if not rate_limiter.is_allowed(user.id, tool.name, tool.rate_limit):
        return PermissionResult(
            decision=Decision.RATE_LIMITED,
            reason=f"'{tool.name}' has hit its rate limit of {tool.rate_limit} calls per minute."
        )

    if tool.requires_approval:
        return PermissionResult(
            decision=Decision.NEEDS_APPROVAL,
            reason=f"'{tool.name}' is high risk and requires human approval."
        )

    if tool.requires_confirmation:
        return PermissionResult(
            decision=Decision.NEEDS_CONFIRMATION,
            reason=f"'{tool.name}' is medium risk and requires confirmation."
        )

    return PermissionResult(
        decision=Decision.ALLOWED,
        reason=f"'{tool.name}' is low risk and {user.role.value} is allowed."
    )