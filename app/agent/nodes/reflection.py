from app.agent.llm import call_llm
from app.agent.prompts import build_reflection_prompt, build_retry_feedback
from app.models.agent_state import AgentState

MAX_RETRIES = 2

def reflect(state: AgentState) -> AgentState:
    if state.tool_error is None:
        return state

    if state.retry_count >= MAX_RETRIES:
        state.final_response = f"Couldn't complete this after repeated attempts: {state.tool_error}"
        return state

    prompt = build_reflection_prompt(state.tool_result, state.tool_error)
    outcome = call_llm(prompt).strip().lower()

    if outcome.startswith("retry"):
        state.retry_count += 1
        state.planning_feedback= build_retry_feedback(
            tool_name=state.selected_tool,
            tool_input=state.tool_input,
            tool_error=state.tool_error
            )
        state.selected_tool = None
        state.tool_input = None
        state.tool_error = None

    else:
        state.final_response = f"Couldn't complete this after repeated attempts: {state.tool_error}"
        
    return state
