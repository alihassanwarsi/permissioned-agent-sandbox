from app.models.agent_state import AgentState
from app.permissions.checker import Decision
from app.tools.registry import ToolRegistry

def execute_tool(state: AgentState, registry: ToolRegistry) -> AgentState:
    if not state.selected_tool or state.decision != Decision.ALLOWED:
        return state

    tool = registry.get(state.selected_tool)

    try:
        result = tool.handler(tool.input_schema(**(state.tool_input or {})))
        state.tool_result = result.model_dump()

    except Exception as e:
        state.tool_error = str(e)
        
    return state
