from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agent.graph import get_trace_store, run_agent, resume_agent
from app.agent.nodes.intake import intake
from app.approval.queue import ApprovalQueue
from app.models.user import Role, User
from app.models.approval import ApprovalStatus
from app.observability.analytics import compute_safety_stats
from app.tools.registry_setup import build_default_registry
from app.permissions.rate_limiter import RateLimiter

app = FastAPI(title="Permissioned Agent Sandbox")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_registry = build_default_registry()
_queue = ApprovalQueue()
_rate_limiter = RateLimiter()

class RunRequest(BaseModel):
    user_message: str
    role: Role

class ResolveRequest(BaseModel):
    outcome: str
    decided_by: str
    note: Optional[str] = None
    modified_input: Optional[dict[str, Any]] = None

def _span_to_dict(span) -> dict:
    return {
        "name": span.name,
        "start_time": span.start_time,
        "end_time": span.end_time,
        "attributes": dict(span.attributes),
    }

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/run")
def run(request: RunRequest):
    user = User(id="user", name="Ali", role=request.role)
    state = intake(request.user_message, user)
    return run_agent(state, _registry, _queue, _rate_limiter)

@app.get("/approvals")
def list_approvals():
    return _queue.list_pending()

@app.post("/approvals/{request_id}/resolve")
def resolve_approval(request_id: str, body: ResolveRequest):
    try:
        pending = _queue.get(request_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="No such approval request")

    if pending.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=409, detail="Approval request has already been resolved")

    decision = {
        "outcome": body.outcome,
        "decided_by": body.decided_by,
        "note": body.note,
        "modified_input": body.modified_input,
    }

    return resume_agent(pending.thread_id, decision, _registry, _queue, _rate_limiter)

@app.get("/traces")
def list_traces():
    return get_trace_store().list_trace_ids()

@app.get("/traces/{trace_id}")
def get_trace(trace_id: str):
    spans = get_trace_store().get_trace(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="No such trace")
    return [_span_to_dict(s) for s in spans]

@app.get("/analytics")
def get_analytics():
    return compute_safety_stats(get_trace_store(), _queue)