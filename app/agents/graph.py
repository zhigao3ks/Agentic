"""LangGraph 工作流组装。"""

from langgraph.graph import END, StateGraph

from app.agents.answer_generator import generate_answer
from app.agents.mcp_tool_agent import execute_tools
from app.agents.query_analyzer import analyze_query
from app.agents.retriever import retrieve
from app.agents.state import AgentState, make_initial_state
from app.agents.tool_planner import plan_tools
from app.agents.verifier import verify


def _needs_tools(state: AgentState) -> str:
    """条件路由：是否需要工具调用。"""
    analysis = state.get("query_analysis", {})
    if analysis.get("needs_tools"):
        return "tool_planner"
    return "retriever"


def _has_tool_calls(state: AgentState) -> str:
    """条件路由：是否有具体的工具调用计划。"""
    if state.get("tool_calls"):
        return "mcp_tool_agent"
    return "retriever"


def build_agent_graph() -> StateGraph:
    """构建 Agent 工作流图。"""
    workflow = StateGraph(AgentState)

    workflow.add_node("query_analyzer", _wrap(analyze_query))
    workflow.add_node("retriever", _wrap_retriever)
    workflow.add_node("tool_planner", _wrap(plan_tools))
    workflow.add_node("mcp_tool_agent", _wrap(execute_tools))
    workflow.add_node("answer_generator", _wrap(generate_answer))
    workflow.add_node("verifier", _wrap(verify))

    workflow.set_entry_point("query_analyzer")

    workflow.add_conditional_edges("query_analyzer", _needs_tools, {
        "tool_planner": "tool_planner",
        "retriever": "retriever",
    })
    workflow.add_conditional_edges("tool_planner", _has_tool_calls, {
        "mcp_tool_agent": "mcp_tool_agent",
        "retriever": "retriever",
    })
    workflow.add_edge("mcp_tool_agent", "answer_generator")
    workflow.add_edge("retriever", "answer_generator")
    workflow.add_edge("answer_generator", "verifier")
    workflow.add_edge("verifier", END)

    return workflow


async def run_agent(
    query: str,
    kb_id: str,
    session_id: str | None = None,
    db=None,
    enable_verifier: bool = True,
    enable_tools: bool = True,
) -> AgentState:
    """执行 Agent 工作流，返回最终状态。"""
    workflow = StateGraph(AgentState)

    workflow.add_node("query_analyzer", _wrap(analyze_query))
    workflow.add_node("retriever", _wrap_retriever_factory(db))
    workflow.add_node("answer_generator", _wrap(generate_answer))

    if enable_tools:
        workflow.add_node("tool_planner", _wrap(plan_tools))
        workflow.add_node("mcp_tool_agent", _wrap(execute_tools))

    if enable_verifier:
        workflow.add_node("verifier", _wrap(verify))

    workflow.set_entry_point("query_analyzer")

    if enable_tools:
        workflow.add_conditional_edges("query_analyzer", _needs_tools, {
            "tool_planner": "tool_planner",
            "retriever": "retriever",
        })
        workflow.add_conditional_edges("tool_planner", _has_tool_calls, {
            "mcp_tool_agent": "mcp_tool_agent",
            "retriever": "retriever",
        })
        workflow.add_edge("mcp_tool_agent", "answer_generator")
    else:
        workflow.add_edge("query_analyzer", "retriever")

    workflow.add_edge("retriever", "answer_generator")

    if enable_verifier:
        workflow.add_edge("answer_generator", "verifier")
        workflow.add_edge("verifier", END)
    else:
        workflow.add_edge("answer_generator", END)

    graph = workflow.compile()
    initial = make_initial_state(query, kb_id, session_id)
    result = await graph.ainvoke(initial, {"recursion_limit": initial["max_steps"]})
    return result


def _wrap(fn):
    async def wrapper(state: AgentState):
        return await fn(state)
    return wrapper


def _wrap_retriever(state: AgentState):
    return retrieve(state, db=None)


def _wrap_retriever_factory(db):
    async def wrapper(state: AgentState):
        return await retrieve(state, db=db)
    return wrapper
