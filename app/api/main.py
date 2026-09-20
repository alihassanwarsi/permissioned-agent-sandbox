from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent.graph import run_agent, resume_agent
from app.agent.nodes.intake import intake
from app.approval.queue import ApprovalQueue
from app.models.user import Role, User
from app.tools.registry_setup import build_default_registry

app = FastAPI(title="Permissioned Agent Sandbox")

_registry = build_default_registry()
_queue = ApprovalQueue()

class RunRequest(BaseModel):
    user_message: str
    role: Role


class ResolveRequest(BaseModel):
    outcome: str
    decided_by: str
    note: Optional[str] = None
    modified_input: Optional[dict[str, Any]] = None

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/run")
def run(request: RunRequest):
    user = User(id="user", name="Ali", role=request.role)
    state = intake(request.user_message, user)
    return run_agent(state, _registry, _queue)

@app.get("/approvals")
def list_approvals():
    return _queue.list_pending()

@app.post("/approvals/{request_id}/resolve")
def resolve_approval(request_id: str, body: ResolveRequest):
    try:
        pending = _queue.get(request_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="No such approval request")

    decision = {
        "outcome": body.outcome,
        "decided_by": body.decided_by,
        "note": body.note,
        "modified_input": body.modified_input,
    }
    return resume_agent(pending.thread_id, decision, _registry, _queue)