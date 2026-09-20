from app.approval.queue import ApprovalQueue
from app.models.approval import ApprovalOutcome, ApprovalStatus
from app.observability.trace_store import InMemoryTraceStore

def compute_safety_stats(trace_store: InMemoryTraceStore, queue: ApprovalQueue) -> dict:
    all_spans = [span for trace_id in trace_store.list_trace_ids() for span in trace_store.get_trace(trace_id)]

    total_nodes_run = len(all_spans)

    errors = sum(1 for s in all_spans if s.attributes.get("status") == "error")
    denials = sum(1 for s in all_spans if s.attributes.get("decision") == "denied")

    tool_counts: dict[str, int] = {}

    for s in all_spans:
        tool = s.attributes.get("tool.selected")
        if tool:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

    resolved_requests = [r for r in queue.all_requests() if r.status == ApprovalStatus.RESOLVED]

    approved = sum(1 for r in resolved_requests if r.outcome == ApprovalOutcome.APPROVED)
    total_resolved = len(resolved_requests)
    approval_rate = approved / total_resolved if total_resolved else None

    return {
        "total_nodes_run": total_nodes_run,
        "errors": errors,
        "denials": denials,
        "tool_usage": tool_counts,
        "approval_rate": approval_rate,
        "total_approval_requests": total_resolved
    }