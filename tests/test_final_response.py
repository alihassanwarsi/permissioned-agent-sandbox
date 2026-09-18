from unittest.mock import patch
from app.agent.nodes.final_response import final_response
from app.models.agent_state import AgentState
from app.models.user import Role, User
from app.permissions.checker import Decision

def make_state(**kwargs):
    defaults = dict(
        task_id="1",
        user_message="x",
        user=User(id="1", name="test", role=Role.ANALYST),
    )
    defaults.update(kwargs)
    return AgentState(**defaults)

def test_already_has_response_passes_through():
    state = final_response(make_state(final_response="already done"))
    assert state.final_response == "already done"

def test_denied_uses_fixed_text_no_llm():
    state = final_response(make_state(decision=Decision.DENIED, decision_reason="not your role"))
    assert "not your role" in state.final_response

def test_needs_approval_uses_fixed_text_no_llm():
    state = final_response(make_state(decision=Decision.NEEDS_APPROVAL, decision_reason="high risk tool"))
    assert "high risk tool" in state.final_response

@patch("app.agent.nodes.final_response.call_llm")
def test_tool_result_uses_llm(mock_call_llm):
    mock_call_llm.return_value = "The file says hello."
    state = final_response(make_state(tool_result={"content": "hello"}))
    assert state.final_response == "The file says hello."

@patch("app.agent.nodes.final_response.call_llm")
def test_no_tool_needed_uses_llm(mock_call_llm):
    mock_call_llm.return_value = "2 + 2 is 4."
    state = final_response(make_state())
    assert state.final_response == "2 + 2 is 4."