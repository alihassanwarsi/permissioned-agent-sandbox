import json
from pydantic import ValidationError
from app.agent.llm import call_llm
from app.agent.prompts import build_planning_prompt
from app.agent.tool_intent import get_explicit_tool_request
from app.models.agent_state import AgentState
from app.models.plan import PlanOutput
from app.tools.registry import ToolRegistry

def plan(state: AgentState, registry: ToolRegistry) -> AgentState:
    explicit_tool = get_explicit_tool_request(state.user_message)

    if explicit_tool == "web_search" and not state.planning_feedback:
        state.plan = "User explicitly requested a web search."
        state.selected_tool = "web_search"
        state.tool_input = {
            "query": state.user_message,
            "max_results": 5,
        }
        return state
    
    prompt = build_planning_prompt(state.user_message, registry, planning_feedback=state.planning_feedback)

    raw_response = call_llm(prompt)

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        state.plan = raw_response
        state.selected_tool = None
        state.tool_input = None
        return state

    try:
        plan_output = PlanOutput.model_validate(parsed)
    except ValidationError:
        state.plan = raw_response
        state.selected_tool = None
        state.tool_input = None
        return state

    state.plan = plan_output.reasoning
    state.selected_tool = plan_output.tool
    state.tool_input = plan_output.input

    return state