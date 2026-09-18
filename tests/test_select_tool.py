from app.agent.nodes.select_tool import select_tool
from app.models.agent_state import AgentState
from app.models.user import Role, User
from app.tools.registry_setup import build_default_registry

def make_state(tool=None, tool_input=None):
    return AgentState(
        task_id="1",
        user_message="x",
        user=User(id="1", name="test", role=Role.ANALYST),
        selected_tool=tool,
        tool_input=tool_input
    )

def test_no_tool_needed_passes_through():
    state = select_tool(make_state(tool=None), build_default_registry())
    assert state.tool_error is None

def test_valid_tool_and_input_passes():
    state = select_tool(
        make_state(tool="file_reader", tool_input={"path": "notes.txt"}),
        build_default_registry(),
    )
    assert state.tool_error is None
    assert state.selected_tool == "file_reader"

def test_unknown_tool_name_errors():
    state = select_tool(
        make_state(tool="delete_everything", tool_input={}),
        build_default_registry(),
    )
    assert state.tool_error is not None
    assert state.selected_tool is None

def test_invalid_input_shape_errors():
    state = select_tool(
        make_state(tool="file_reader", tool_input={"wrong_field": "x"}),
        build_default_registry(),
    )
    assert state.tool_error is not None
    assert state.selected_tool is None