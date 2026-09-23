from app.agent.llm import call_llm
from app.agent.prompts import build_direct_answer_prompt, build_result_prompt
from app.models.agent_state import AgentState
from app.permissions.checker import Decision

def final_response(state: AgentState) -> AgentState:
    if state.final_response is not None:
        return state

    if state.decision == Decision.DENIED:
        state.final_response = f"I'm not able to do that: {state.decision_reason}"
        return state

    if state.decision == Decision.RATE_LIMITED:
        state.final_response = f"Please wait before trying again: {state.decision_reason}"
        return state

    if state.decision in (Decision.NEEDS_CONFIRMATION, Decision.NEEDS_APPROVAL):
        state.final_response = f"Before I can do that: {state.decision_reason}"
        return state

    if state.tool_result is not None:
        prompt = build_result_prompt(state.user_message, state.tool_result)
        state.final_response = call_llm(prompt)
        return state

    prompt = build_direct_answer_prompt(state.user_message)
    state.final_response = call_llm(prompt)
    return state