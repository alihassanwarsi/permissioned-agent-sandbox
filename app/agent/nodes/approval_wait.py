import uuid
from langgraph.types import interrupt
from app.approval.queue import ApprovalQueue
from app.models.agent_state import AgentState
from app.models.approval import ApprovalOutcome, ApprovalRequest
from app.permissions.checker import Decision
from app.tools.registry import ToolRegistry

def approval_wait(state: AgentState, registry: ToolRegistry, queue: ApprovalQueue) -> AgentState:
    tool = registry.get(state.selected_tool)

    if not state.approval_request_id:
        state.approval_request_id = str(uuid.uuid4())
        request = ApprovalRequest(
            request_id=state.approval_request_id,
            thread_id=state.task_id,
            tool_name=tool.name,
            tool_input=state.tool_input or {},
            risk_level=tool.risk_level,
            reasoning=state.plan or "",
        )
        queue.add(request)

    decision = interrupt({
        "request_id": state.approval_request_id,
        "task_id": state.task_id,
        "selected_tool": state.selected_tool,
        "tool_input": state.tool_input,
        "decision_reason": state.decision_reason,
    })

    outcome = ApprovalOutcome(decision.get("outcome"))
    queue.resolve(
        state.approval_request_id,
        outcome=outcome,
        decided_by=decision.get("decided_by", "unknown"),
        note=decision.get("note"),
        modified_input=decision.get("modified_input"),
    )

    if outcome == ApprovalOutcome.APPROVED:
        state.decision = Decision.ALLOWED
        state.decision_reason = decision.get("note", state.decision_reason)

    elif outcome == ApprovalOutcome.MODIFIED:
        state.decision = Decision.ALLOWED
        state.tool_input = decision.get("modified_input", state.tool_input)

    elif outcome == ApprovalOutcome.REPLAN:
        state.selected_tool = None
        state.tool_input = None
        state.decision = None
        state.approval_request_id = None

    else:
        state.final_response = f"This action was rejected: {decision.get('note', 'no reason given')}"

    return state