from langgraph.types import interrupt
from app.models.agent_state import AgentState
from app.permissions.checker import Decision

def approval_wait(state: AgentState) -> AgentState:
    decision = interrupt({
        "task_id": state.task_id,
        "selected_tool": state.selected_tool,
        "tool_input": state.tool_input,
        "decision_reason": state.decision_reason,
    })

    if decision.get("outcome") == "approved":
        state.decision = Decision.ALLOWED
        state.decision_reason = decision.get("note", state.decision_reason)
        state.tool_input = decision.get("modified_input", state.tool_input)
    else:
        state.final_response = f"This action was rejected: {decision.get('note', 'no reason given')}"

    return state