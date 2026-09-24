from app.approval.queue import ApprovalQueue
from app.models.approval import ApprovalKind, ApprovalOutcome, ApprovalRequest
from app.models.tool_spec import RiskLevel
from app.observability.analytics import compute_safety_stats
from app.observability.trace_store import InMemoryTraceStore

def test_empty_stores_give_zero_stats():
    stats = compute_safety_stats(InMemoryTraceStore(), ApprovalQueue())
    assert stats["total_nodes_run"] == 0
    assert stats["approval_rate"] is None

def test_approval_rate_reflects_resolved_requests():
    queue = ApprovalQueue()
    queue.add(ApprovalRequest(
        request_id="1", thread_id="t1", kind=ApprovalKind.APPROVAL,
        tool_name="send_email",
        tool_input={}, risk_level=RiskLevel.HIGH, reasoning="x",
    ))
    queue.resolve("1", ApprovalOutcome.APPROVED, decided_by="ali")

    stats = compute_safety_stats(InMemoryTraceStore(), queue)
    assert stats["approval_rate"] == 1.0
    assert stats["total_approval_requests"] == 1