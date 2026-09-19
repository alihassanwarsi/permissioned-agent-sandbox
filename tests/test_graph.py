from unittest.mock import patch
from app.agent.graph import build_graph
from app.agent.nodes.intake import intake
from app.models.user import Role, User
from app.tools.registry_setup import build_default_registry

@patch("app.agent.nodes.plan.call_llm")
@patch("app.agent.nodes.final_response.call_llm")
def test_low_risk_tool_runs_end_to_end(mock_final_llm, mock_plan_llm, tmp_path, monkeypatch):
    monkeypatch.setattr("app.tools.file_reader.SANDBOX_DIR", tmp_path)
    (tmp_path / "notes.txt").write_text("hello world")

    mock_plan_llm.return_value = (
        '{"tool": "file_reader", "input": {"path": "notes.txt"}, '
        '"reasoning": "user wants the file"}'
    )
    mock_final_llm.return_value = "The file says: hello world"

    state = intake("read notes.txt", User(id="1", name="test", role=Role.ANALYST))
    graph = build_graph(build_default_registry())
    result = graph.invoke(state)

    assert result["final_response"] == "The file says: hello world"
    assert result["decision"].value == "allowed"

@patch("app.agent.nodes.plan.call_llm")
def test_denied_role_stops_before_execution(mock_plan_llm):
    mock_plan_llm.return_value = (
        '{"tool": "send_email", "input": {"to": "x@x.com", "subject": "hi", "body": "hi"}, '
        '"reasoning": "user wants to send email"}'
    )

    state = intake("email someone", User(id="1", name="test", role=Role.VIEWER))
    graph = build_graph(build_default_registry())
    result = graph.invoke(state)

    assert result["decision"].value == "denied"
    assert "not able to do that" in result["final_response"].lower()