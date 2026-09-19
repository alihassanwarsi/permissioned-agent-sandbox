from unittest.mock import patch
from app.approval.queue import ApprovalQueue
from app.agent.nodes.approval_wait import approval_wait
from app.models.agent_state import AgentState
from app.models.approval import ApprovalOutcome
from app.models.user import Role, User
from app.permissions.checker import Decision
from app.tools.registry_setup import build_default_registry

def make_state():
    return AgentState(
        task_id="t1",
        user_message="email someone",
        user=User(id="1", name="test", role=Role.ADMIN),
        selected_tool="send_email",
        tool_input={"to": "x@x.com", "subject": "hi", "body": "hi"},
        decision=Decision.NEEDS_APPROVAL,
        decision_reason="high risk",
        plan="user wants to email someone",
    )

@patch("app.agent.nodes.approval_wait.interrupt")
def test_modified_updates_input_and_allows(mock_interrupt):
    mock_interrupt.return_value = {
        "outcome": "modified",
        "decided_by": "ali",
        "modified_input": {"to": "x@x.com", "subject": "Updated", "body": "hi"},
    }

    queue = ApprovalQueue()
    state = approval_wait(make_state(), build_default_registry(), queue)

    assert state.decision == Decision.ALLOWED
    assert state.tool_input["subject"] == "Updated"

@patch("app.agent.nodes.approval_wait.interrupt")
def test_replan_clears_tool_selection(mock_interrupt):
    mock_interrupt.return_value = {"outcome": "replan", "decided_by": "ali"}

    queue = ApprovalQueue()
    state = approval_wait(make_state(), build_default_registry(), queue)

    assert state.selected_tool is None
    assert state.tool_input is None
    assert state.decision is None

@patch("app.agent.nodes.approval_wait.interrupt")
def test_resolved_request_recorded_in_queue(mock_interrupt):
    mock_interrupt.return_value = {"outcome": "approved", "decided_by": "ali"}

    queue = ApprovalQueue()
    approval_wait(make_state(), build_default_registry(), queue)

    resolved = queue.get(list(queue._requests.keys())[0])
    assert resolved.outcome == ApprovalOutcome.APPROVED
    assert resolved.decided_by == "ali"