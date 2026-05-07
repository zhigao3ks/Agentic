"""流式 Agent 工作流 —— 通过 WebSocket 推送中间事件。"""

import json
import uuid

from app.agents.state import make_initial_state
from app.schemas.ws_events import (
    answer_delta,
    citation_event,
    done_event,
    error_event,
    mcp_tool_call,
    mcp_tool_result,
    query_analyzed,
    retrieval_completed,
    retrieval_started,
)
from app.services import context_builder, dependencies
from app.services.llm.base import LLMService
from app.services.retrieval.hybrid_pipeline import hybrid_search
from app.services.ws_manager import ws_manager


async def run_streaming_agent(
    query: str,
    kb_id: str,
    session_id: str,
    db,
    enable_tools: bool = True,
) -> str:
    """执行流式 Agent 工作流，通过 WebSocket 推送事件，返回完整回答文本。"""
    state = make_initial_state(query, kb_id, session_id)

    try:
        # 1. Query Analyzer
        from app.agents.query_analyzer import analyze_query
        result = await analyze_query(state)
        state.update(result)
        await ws_manager.send_event(session_id, query_analyzed(
            state["query_analysis"].get("query_type", "knowledge_qa"),
            state["query_analysis"].get("needs_tools", False),
        ))

        # 2. Tool Planning (if needed)
        if enable_tools and state["query_analysis"].get("needs_tools"):
            from app.agents.tool_planner import plan_tools
            result = await plan_tools(state)
            state.update(result)

            if state.get("tool_calls"):
                from app.agents.mcp_tool_agent import execute_tools

                for tc in state["tool_calls"]:
                    await ws_manager.send_event(session_id, mcp_tool_call(
                        tc["tool"], tc.get("arguments", {})
                    ))

                result = await execute_tools(state)
                state.update(result)

                for tr in state.get("tool_results", []):
                    await ws_manager.send_event(session_id, mcp_tool_result(
                        tr["tool"], tr.get("is_error", False)
                    ))

        # 3. Retrieval
        await ws_manager.send_event(session_id, retrieval_started())
        chunks = await hybrid_search(query=query, kb_id=uuid.UUID(kb_id), db=db, top_k=8)
        state["retrieved_chunks"] = chunks
        await ws_manager.send_event(session_id, retrieval_completed(len(chunks)))

        # 4. Answer Generation (streaming)
        if not chunks:
            full_answer = "当前知识库中没有找到相关信息，请尝试上传相关文档后再提问。"
            for char in full_answer:
                await ws_manager.send_event(session_id, answer_delta(char))
        else:
            context = context_builder.build_context(chunks)
            prompt = _build_prompt(context, query)

            llm = _get_llm()
            full_answer = ""
            async for token in llm.generate_stream(prompt, system_prompt=_SYSTEM_PROMPT):
                full_answer += token
                await ws_manager.send_event(session_id, answer_delta(token))

        # 5. Citations
        from app.services import citation
        citations = citation.extract_citations(full_answer, chunks)
        await ws_manager.send_event(session_id, citation_event(citations))

        # 6. Done
        await ws_manager.send_event(session_id, done_event(full_answer))
        return full_answer

    except Exception as e:
        await ws_manager.send_event(session_id, error_event(str(e)))
        return ""


_SYSTEM_PROMPT = "你是一个基于企业知识库的智能问答助手。请严格根据上下文信息回答问题。回答时标注引用编号 [1]、[2]。"


def _build_prompt(context: str, query: str) -> str:
    return f"上下文信息：\n\n{context}\n\n用户问题：{query}\n\n请基于以上上下文回答问题，并标注引用编号。"


def _get_llm() -> LLMService:
    if dependencies.get_embedding_service():  # dev mode detection
        from app.services.llm.fake import FakeLLMService
        return FakeLLMService()
    from app.services.llm.openai_llm import OpenAILLMService
    return OpenAILLMService()
