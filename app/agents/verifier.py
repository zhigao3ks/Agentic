"""Verifier Agent —— 校验回答是否有证据支持，引用是否准确。"""

from app.agents.state import AgentState
from app.services.llm.base import LLMService

VERIFY_PROMPT = """请验证以下回答是否得到了上下文信息的支持。

上下文信息：
{context}

回答：
{answer}

引用列表：
{citations}

请返回 JSON 格式的验证结果：
{{
  "result": "pass|partial|fail",
  "issues": ["问题描述1", "问题描述2"],
  "supported_claims": 0,
  "total_claims": 0
}}

只返回 JSON，不要其他内容。"""


async def verify(
    state: AgentState,
    llm: LLMService | None = None,
) -> dict:
    """验证回答质量，返回验证结果。"""
    if llm is None:
        from app.services.llm.fake import FakeLLMService
        llm = FakeLLMService()

    answer = state.get("answer", "")
    chunks = state.get("retrieved_chunks", [])
    citations_list = state.get("citations", [])

    if not answer or not chunks:
        return {
            "verification": {"result": "fail", "issues": ["No answer or evidence to verify"]},
            "messages": [{"role": "verifier", "content": "nothing to verify"}],
            "step_count": state["step_count"] + 1,
        }

    from app.services import context_builder
    context = context_builder.build_context(chunks)
    prompt = VERIFY_PROMPT.format(
        context=context,
        answer=answer,
        citations=citations_list,
    )

    import json
    raw = await llm.generate(prompt)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"result": "partial", "issues": ["Could not parse verification result"]}

    result.setdefault("result", "partial")
    result.setdefault("issues", [])

    is_success = result["result"] == "pass"

    return {
        "verification": result,
        "status": "completed" if is_success else state.get("status", "running"),
        "messages": [{"role": "verifier", "content": str(result)}],
        "step_count": state["step_count"] + 1,
    }
