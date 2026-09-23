from app.models.agent_state import AgentState
from app.permissions.checker import check_permission
from app.permissions.rate_limiter import RateLimiter
from app.tools.registry import ToolRegistry

def permission_check(state: AgentState, registry: ToolRegistry, rate_limiter: RateLimiter) -> AgentState:
    if not state.selected_tool:
        return state

    tool = registry.get(state.selected_tool)
    result = check_permission(state.user, tool, rate_limiter)

    state.decision = result.decision
    state.decision_reason = result.reason
    return state