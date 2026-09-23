from unittest.mock import patch
from app.agent.graph import run_agent, resume_agent
from app.agent.nodes.intake import intake
from app.approval.queue import ApprovalQueue
from app.models.user import Role, User
from app.permissions.rate_limiter import RateLimiter
from app.tools.registry_setup import build_default_registry

@patch("app.agent.nodes.plan.call_llm")
def test_high_risk_tool_pauses_for_approval(mock_plan_llm):
    mock_plan_llm.return_value = (
        '{"tool": "send_email", "input": {"to": "x@x.com", "subject": "hi", "body": "hi"}, '
        '"reasoning": "user wants to send an email"}'
    )

    state = intake("email someone", User(id="1", name="test", role=Role.ADMIN))
    result = run_agent(state, build_default_registry(), ApprovalQueue(), RateLimiter())

    assert result["status"] == "awaiting_approval"
    assert "thread_id" in result

@patch("app.agent.nodes.plan.call_llm")
@patch("app.agent.nodes.final_response.call_llm")
def test_approved_task_resumes_and_completes(mock_final_llm, mock_plan_llm):
    mock_plan_llm.return_value = (
        '{"tool": "send_email", "input": {"to": "x@x.com", "subject": "hi", "body": "hi"}, '
        '"reasoning": "user wants to send an email"}'
    )
    mock_final_llm.return_value = "Email sent successfully."

    registry = build_default_registry()
    queue = ApprovalQueue()
    rate_limiter = RateLimiter()
    state = intake("email someone", User(id="1", name="test", role=Role.ADMIN))

    paused = run_agent(state, registry, queue, rate_limiter)
    assert paused["status"] == "awaiting_approval"

    resumed = resume_agent(
        paused["thread_id"],
        {"outcome": "approved", "decided_by": "ali"},
        registry,
        queue,
        rate_limiter,
    )

    assert resumed["status"] == "completed"
    assert resumed["final_response"] == "Email sent successfully."

@patch("app.agent.nodes.plan.call_llm")
def test_rejected_task_resumes_with_denial(mock_plan_llm):
    mock_plan_llm.return_value = (
        '{"tool": "send_email", "input": {"to": "x@x.com", "subject": "hi", "body": "hi"}, '
        '"reasoning": "user wants to send an email"}'
    )

    registry = build_default_registry()
    queue = ApprovalQueue()
    rate_limiter = RateLimiter()
    state = intake("email someone", User(id="1", name="test", role=Role.ADMIN))

    paused = run_agent(state, registry, queue, rate_limiter)
    resumed = resume_agent(
        paused["thread_id"],
        {"outcome": "rejected", "decided_by": "ali", "note": "not needed right now"},
        registry,
        queue,
        rate_limiter,
    )

    assert resumed["status"] == "completed"
    assert "rejected" in resumed["final_response"].lower()