"""Answer Generator Agent —— 基于检索证据生成最终回答。"""

from app.agents.state import AgentState
from app.services import citation, context_builder
from app.services.llm.base import LLMService

GENERATE_PROMPT = """你是一个基于企业知识库的智能问答助手。
请严格根据以下上下文信息回答用户问题。
如果上下文中没有相关信息，请明确告知用户，不要编造答案。
回答时请引用相关上下文编号，例如 [1]、[2]。

上下文信息：

{context}

用户问题：{query}

请基于以上上下文回答问题，并标注引用编号。"""


async def generate_answer(
    state: AgentState,
    llm: LLMService | None = None,
) -> dict:
    """生成回答并提取引用。"""
    if llm is None:
        from app.services.llm.fake import FakeLLMService
        llm = FakeLLMService()

    chunks = state.get("retrieved_chunks", [])

    if not chunks:
        return {
            "answer": "当前知识库中没有找到相关信息，请尝试上传相关文档后再提问。",
            "citations": [],
            "messages": [{"role": "answer_generator", "content": "no evidence found"}],
            "step_count": state["step_count"] + 1,
        }

    context = context_builder.build_context(chunks)
    prompt = GENERATE_PROMPT.format(context=context, query=state["query"])
    answer = await llm.generate(prompt)

    citations_list = citation.extract_citations(answer, chunks)

    return {
        "answer": answer,
        "citations": citations_list,
        "messages": [{"role": "answer_generator", "content": answer[:200]}],
        "step_count": state["step_count"] + 1,
    }
