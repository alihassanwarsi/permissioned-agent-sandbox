from functools import partial
from langgraph.graph import StateGraph, END
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

def build_graph(registry: ToolRegistry):
    graph = StateGraph(AgentState)

    graph.add_node("plan", partial(plan, registry=registry))
    graph.add_node("select_tool", partial(select_tool, registry=registry))
    graph.add_node("permission_check", partial(permission_check, registry=registry))
    graph.add_node("execute_tool", partial(execute_tool, registry=registry))
    graph.add_node("reflection", reflect)
    graph.add_node("approval_wait", approval_wait)
    graph.add_node("final_response", final_response)

    graph.set_entry_point("plan")

    graph.add_conditional_edges("plan", route_after_plan)
    graph.add_conditional_edges("select_tool", route_after_select_tool)
    graph.add_conditional_edges("permission_check", route_after_permission)
    graph.add_conditional_edges("execute_tool", route_after_execute)
    graph.add_conditional_edges("reflection", route_after_reflection)
    graph.add_edge("approval_wait", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()