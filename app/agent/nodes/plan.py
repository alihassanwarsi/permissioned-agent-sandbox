import json
from app.agent.llm import call_llm
from app.agent.prompts import build_planning_prompt
from app.models.agent_state import AgentState
from app.tools.registry import ToolRegistry

def plan(state: AgentState, registry: ToolRegistry) -> AgentState:
    prompt = build_planning_prompt(state.user_message, registry)
    raw_response = call_llm(prompt)

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        state.plan = raw_response
        state.selected_tool = None
        state.tool_input = None
        return state

    state.plan = parsed.get("reasoning")
    state.selected_tool =  parsed.get("tool")
    state.tool_input = parsed.get("input")
    return state