from app.agent.nodes.execute_tool import execute_tool
from app.models.agent_state import AgentState
from app.models.user import Role, User
from app.permissions.checker import Decision
from app.permissions.rate_limiter import RateLimiter
from app.tools.registry_setup import build_default_registry

def make_state(tool=None, tool_input=None, decision=None):
    return AgentState(
        task_id="1",
        user_message="x",
        user=User(id="1", name="test", role=Role.ANALYST),
        selected_tool=tool,
        tool_input=tool_input,
        decision=decision,
    )

def test_skips_when_not_allowed():
    state = execute_tool(
        make_state(tool="send_email", decision=Decision.NEEDS_APPROVAL),
        build_default_registry(),
        RateLimiter(),
    )
    assert state.tool_result is None
    assert state.tool_error is None

def test_runs_allowed_tool_successfully(tmp_path, monkeypatch):
    monkeypatch.setattr("app.tools.file_reader.SANDBOX_DIR", tmp_path)
    (tmp_path / "notes.txt").write_text("hello")

    state = execute_tool(
        make_state(tool="file_reader", tool_input={"path": "notes.txt"}, decision=Decision.ALLOWED),
        build_default_registry(),
        RateLimiter(),
    )
    assert state.tool_error is None
    assert state.tool_result["content"] == "hello"

def test_captures_failure_as_tool_error():
    state = execute_tool(
        make_state(tool="file_reader", tool_input={"path": "ghost.txt"}, decision=Decision.ALLOWED),
        build_default_registry(),
        RateLimiter(),
    )
    assert state.tool_error is not None
    assert state.tool_result is None