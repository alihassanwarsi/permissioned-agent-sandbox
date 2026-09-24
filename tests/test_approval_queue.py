from app.approval.queue import ApprovalQueue
from app.models.approval import ApprovalOutcome, ApprovalRequest, ApprovalKind
from app.models.tool_spec import RiskLevel

def make_request(request_id="1"):
    return ApprovalRequest(
        request_id=request_id,
        thread_id="t1",
        kind=ApprovalKind.APPROVAL,
        tool_name="send_email",
        tool_input={"to": "x@x.com"},
        risk_level=RiskLevel.HIGH,
        reasoning="user wants to send an email",
    )

def test_added_request_appears_in_pending():
    queue = ApprovalQueue()
    queue.add(make_request())
    assert len(queue.list_pending()) == 1

def test_resolved_request_disappears_from_pending():
    queue = ApprovalQueue()
    queue.add(make_request())
    queue.resolve("1", ApprovalOutcome.APPROVED, decided_by="ali")
    assert queue.list_pending() == []

def test_resolve_records_who_and_outcome():
    queue = ApprovalQueue()
    queue.add(make_request())
    resolved = queue.resolve("1", ApprovalOutcome.REJECTED, decided_by="ali", note="not needed")
    assert resolved.decided_by == "ali"
    assert resolved.note == "not needed"

def test_resolve_sets_resolved_at():
    queue = ApprovalQueue()
    queue.add(make_request())
    resolved = queue.resolve("1", ApprovalOutcome.APPROVED, decided_by="ali")
    assert resolved.resolved_at is not None

def test_resolving_already_resolved_request_fails():
    queue = ApprovalQueue()
    queue.add(make_request())

    queue.resolve("1", ApprovalOutcome.APPROVED, decided_by="ali")

    try:
        queue.resolve("1", ApprovalOutcome.REJECTED, decided_by="ali")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "already been resolved" in str(exc)