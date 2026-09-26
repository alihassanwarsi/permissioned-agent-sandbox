from app.models.agent_state import AgentState
from app.permissions.checker import Decision
from app.permissions.rate_limiter import RateLimiter
from app.tools.registry import ToolRegistry

def execute_tool(state: AgentState, registry: ToolRegistry, rate_limiter: RateLimiter) -> AgentState:
    if not state.selected_tool or state.decision != Decision.ALLOWED:
        return state

    tool = registry.get(state.selected_tool)

    try:
        validated_input = tool.input_schema.model_validate(state.tool_input or {})
        result = tool.handler(validated_input)
        validated_output = tool.output_schema.model_validate(result)
        state.tool_result = validated_output.model_dump()
        state.tool_error = None
        rate_limiter.record_call(state.user.id, tool.name)
    except Exception as e:
        state.tool_error = str(e)

    return state