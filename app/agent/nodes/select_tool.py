from pydantic import ValidationError
from app.models.agent_state import AgentState
from app.tools.registry import ToolRegistry

def select_tool(state: AgentState, registry: ToolRegistry) -> AgentState:
    if not state.selected_tool:
        return state
    try:
        tool = registry.get(state.selected_tool)
    except KeyError as e:
        state.tool_error = str(e)
        state.selected_tool = None
        return state

    try:
        tool.input_schema(**(state.tool_input or {}))
    except ValidationError as e:
        state.tool_error = f"Invalid arguments for '{tool.name}': {e}"
        state.selected_tool = None
        return state

    return state