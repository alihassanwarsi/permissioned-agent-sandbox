from unittest.mock import patch
from app.agent.nodes.reflection import reflect
from app.models.agent_state import AgentState
from app.models.user import Role, User

def make_state(tool_error=None, retry_count=0):
    return AgentState(
        task_id="1",
        user_message="x",
        user=User(id="1", name="test", role=Role.ANALYST),
        tool_error=tool_error,
        retry_count=retry_count,
    )

def test_no_error_passes_through():
    state = reflect(make_state(tool_error=None))
    assert state.final_response is None

@patch("app.agent.nodes.reflection.call_llm")
def test_retries_when_llm_says_retry(mock_call_llm):
    mock_call_llm.return_value = "retry"
    state = reflect(make_state(tool_error="timed out", retry_count=0))
    assert state.retry_count == 1
    assert state.tool_error is None
    assert state.selected_tool is None

@patch("app.agent.nodes.reflection.call_llm")
def test_gives_up_when_llm_says_stop(mock_call_llm):
    mock_call_llm.return_value = "stop"
    state = reflect(make_state(tool_error="bad input", retry_count=0))
    assert state.final_response is not None

def test_gives_up_after_max_retries_without_calling_llm():
    state = reflect(make_state(tool_error="still broken", retry_count=2))
    assert state.final_response is not None
    assert "2 attempts" in state.final_response