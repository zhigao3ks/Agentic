"""LangGraph 工作流组装。"""

from langgraph.graph import END, StateGraph

from app.agents.answer_generator import generate_answer
from app.agents.query_analyzer import analyze_query
from app.agents.retriever import retrieve
from app.agents.state import AgentState, make_initial_state
from app.agents.verifier import verify


def build_agent_graph() -> StateGraph:
    """构建 Agent 工作流图。"""
    workflow = StateGraph(AgentState)

    workflow.add_node("query_analyzer", _wrap(analyze_query))
    workflow.add_node("retriever", _wrap_retriever)
    workflow.add_node("answer_generator", _wrap(generate_answer))
    workflow.add_node("verifier", _wrap(verify))

    workflow.set_entry_point("query_analyzer")

    # query_analyzer → retriever → answer_generator → verifier → END
    workflow.add_edge("query_analyzer", "retriever")
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
) -> AgentState:
    """执行 Agent 工作流，返回最终状态。"""
    from langgraph.graph import END

    workflow = StateGraph(AgentState)

    workflow.add_node("query_analyzer", _wrap(analyze_query))
    workflow.add_node("retriever", _wrap_retriever_factory(db))
    workflow.add_node("answer_generator", _wrap(generate_answer))

    if enable_verifier:
        workflow.add_node("verifier", _wrap(verify))
        workflow.set_entry_point("query_analyzer")
        workflow.add_edge("query_analyzer", "retriever")
        workflow.add_edge("retriever", "answer_generator")
        workflow.add_edge("answer_generator", "verifier")
        workflow.add_edge("verifier", END)
    else:
        workflow.set_entry_point("query_analyzer")
        workflow.add_edge("query_analyzer", "retriever")
        workflow.add_edge("retriever", "answer_generator")
        workflow.add_edge("answer_generator", END)

    graph = workflow.compile()
    initial = make_initial_state(query, kb_id, session_id)
    result = await graph.ainvoke(initial, {"recursion_limit": initial["max_steps"]})
    return result


def _wrap(fn):
    """将节点函数包装为 LangGraph 可调用形式。"""
    async def wrapper(state: AgentState):
        return await fn(state)
    return wrapper


def _wrap_retriever(state: AgentState):
    return retrieve(state, db=None)


def _wrap_retriever_factory(db):
    async def wrapper(state: AgentState):
        return await retrieve(state, db=db)
    return wrapper
