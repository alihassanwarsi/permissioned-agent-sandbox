from unittest.mock import patch
from app.agent.nodes.plan import plan
from app.models.agent_state import AgentState
from app.models.user import Role, User
from app.tools.registry_setup import build_default_registry

def make_state():
    return AgentState(
        task_id="1",
        user_message="read notes.txt",
        user=User(id="1", name="test", role=Role.ANALYST),
    )

@patch("app.agent.nodes.plan.call_llm")
def test_plan_parses_valid_json(mock_call_llm):
    mock_call_llm.return_value = (
        '{"tool": "file_reader", "input": {"path": "notes.txt"}, '
        '"reasoning": "user wants to read a file"}'
    )
    state = plan(make_state(), build_default_registry())
    assert state.selected_tool == "file_reader"
    assert state.tool_input == {"path": "notes.txt"}

@patch("app.agent.nodes.plan.call_llm")
def test_plan_handles_bad_json(mock_call_llm):
    mock_call_llm.return_value = "not json at all"
    state = plan(make_state(), build_default_registry())
    assert state.selected_tool is None
    assert state.plan == "not json at all"