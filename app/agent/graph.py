import uuid
from functools import partial
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from app.agent.nodes.permission_check import permission_check
from app.agent.nodes.execute_tool import execute_tool
from app.agent.nodes.final_response import final_response
from app.agent.nodes.approval_wait import approval_wait
from app.agent.nodes.plan import plan
from app.agent.nodes.reflection import reflect
from app.agent.nodes.select_tool import select_tool
from app.models.agent_state import AgentState
from app.permissions.checker import Decision
from app.tools.registry import ToolRegistry
from app.approval.queue import ApprovalQueue
from app.observability.tracing import build_tracer_provider, get_tracer
from app.observability.trace_store import InMemoryTraceStore
from app.observability.trace_node import traced_node

_checkpointer = MemorySaver()
_trace_store = InMemoryTraceStore()
_tracer_provider = build_tracer_provider(exporters=[ConsoleSpanExporter(), _trace_store])
_tracer = get_tracer(_tracer_provider)

def get_trace_store() -> InMemoryTraceStore:
    return _trace_store

def route_after_plan(state: AgentState) -> str:
    if state.selected_tool:
        return "select_tool"
    return "final_response"

def route_after_select_tool(state: AgentState) -> str:
    if state.selected_tool:
        return "permission_check"
    return "final_response"

def route_after_permission(state: AgentState) -> str:
    return {
        Decision.ALLOWED: "execute_tool",
        Decision.DENIED: "final_response",
        Decision.NEEDS_CONFIRMATION: "approval_wait",
        Decision.NEEDS_APPROVAL: "approval_wait",
    }[state.decision]

def route_after_execute(state: AgentState) -> str:
    if state.tool_error:
        return "reflection"
    return "final_response"

def route_after_reflection(state: AgentState) -> str:
    if state.final_response is not None:
        return "final_response"
    return "plan"

def route_after_approval(state: AgentState) -> str:
    if state.final_response is not None:
        return "final_response"
    if state.selected_tool is None:
        return "plan"
    return "execute_tool"

def build_graph(registry: ToolRegistry, queue: ApprovalQueue):
    graph = StateGraph(AgentState)

    graph.add_node("plan", traced_node(_tracer, "plan", partial(plan, registry=registry)))
    graph.add_node("select_tool", traced_node(_tracer, "select_tool", partial(select_tool, registry=registry)))
    graph.add_node("permission_check", traced_node(_tracer, "permission_check", partial(permission_check, registry=registry)))
    graph.add_node("execute_tool", traced_node(_tracer, "execute_tool", partial(execute_tool, registry=registry)))
    graph.add_node("reflection", traced_node(_tracer, "reflection", reflect))
    graph.add_node("approval_wait", traced_node(_tracer, "approval_wait", partial(approval_wait, registry=registry, queue=queue)))
    graph.add_node("final_response", traced_node(_tracer, "final_response", final_response))

    graph.set_entry_point("plan")

    graph.add_conditional_edges("plan", route_after_plan)
    graph.add_conditional_edges("select_tool", route_after_select_tool)
    graph.add_conditional_edges("permission_check", route_after_permission)
    graph.add_conditional_edges("execute_tool", route_after_execute)
    graph.add_conditional_edges("reflection", route_after_reflection)
    graph.add_conditional_edges("approval_wait", route_after_approval)
    graph.add_edge("final_response", END)

    return graph.compile(checkpointer=_checkpointer)

def run_agent(state: AgentState, registry: ToolRegistry, queue: ApprovalQueue) -> dict:
    compiled_graph = build_graph(registry, queue)
    thread_id = state.task_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    result = compiled_graph.invoke(state, config=config)

    if "__interrupt__" in result:
        return {"status": "awaiting_approval", "thread_id": thread_id}
    return {"status": "completed", "final_response": result["final_response"]}

def resume_agent(thread_id: str, decision: dict, registry: ToolRegistry, queue: ApprovalQueue) -> dict:
    compiled_graph = build_graph(registry, queue)
    config = {"configurable": {"thread_id": thread_id}}

    result = compiled_graph.invoke(Command(resume=decision), config=config)

    if "__interrupt__" in result:
        return {"status": "awaiting_approval", "thread_id": thread_id}
    return {"status": "completed", "final_response": result["final_response"]}