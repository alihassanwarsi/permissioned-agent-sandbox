from app.agent.nodes.permission_check import permission_check
from app.models.agent_state import AgentState
from app.models.user import Role, User
from app.permissions.checker import Decision
from app.tools.registry_setup import build_default_registry

def make_state(tool=None, role=Role.ANALYST):
    return AgentState(
        task_id="1",
        user_message="x",
        user=User(id="1", name="test", role=role),
        selected_tool=tool,
    )

def test_no_tool_selected_skips_check():
    state = permission_check(make_state(tool=None), build_default_registry())
    assert state.decision is None

def test_low_risk_tool_gets_allowed():
    state = permission_check(make_state(tool="file_reader"), build_default_registry())
    assert state.decision == Decision.ALLOWED

def test_high_risk_tool_needs_approval():
    state = permission_check(
        make_state(tool="send_email", role=Role.ADMIN), build_default_registry()
    )
    assert state.decision == Decision.NEEDS_APPROVAL