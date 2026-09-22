from unittest.mock import patch
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.agent.nodes.plan.call_llm")
@patch("app.agent.nodes.final_response.call_llm")
def test_run_low_risk_tool_completes(mock_final_llm, mock_plan_llm, tmp_path, monkeypatch):
    monkeypatch.setattr("app.tools.file_reader.SANDBOX_DIR", tmp_path)
    (tmp_path / "notes.txt").write_text("hello world")

    mock_plan_llm.return_value = (
        '{"tool": "file_reader", "input": {"path": "notes.txt"}, '
        '"reasoning": "user wants the file"}'
    )
    mock_final_llm.return_value = "The file says: hello world"

    response = client.post("/run", json={"user_message": "read notes.txt", "role": "analyst"})

    assert response.status_code == 200
    assert response.json()["final_response"] == "The file says: hello world"

@patch("app.agent.nodes.plan.call_llm")
def test_run_high_risk_tool_pauses_and_shows_in_approvals(mock_plan_llm):
    mock_plan_llm.return_value = (
        '{"tool": "send_email", "input": {"to": "x@x.com", "subject": "hi", "body": "hi"}, '
        '"reasoning": "user wants to email someone"}'
    )

    run_response = client.post("/run", json={"user_message": "email someone", "role": "admin"})
    assert run_response.json()["status"] == "awaiting_approval"

    approvals = client.get("/approvals").json()
    assert len(approvals) >= 1
    assert approvals[-1]["tool_name"] == "send_email"

def test_resolve_unknown_approval_returns_404():
    response = client.post(
        "/approvals/does-not-exist/resolve",
        json={"outcome": "approved", "decided_by": "ali"},
    )
    assert response.status_code == 404

def test_unknown_trace_returns_404():
    response = client.get("/traces/does-not-exist")
    assert response.status_code == 404