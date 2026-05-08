"""Query Analyzer Agent —— 分析用户问题意图和类型。"""

from app.agents.state import AgentState
from app.services.dependencies import get_embedding_service
from app.services.llm.base import LLMService

ANALYZE_PROMPT = """分析以下用户问题，返回 JSON 格式的分析结果：

{{
  "query_type": "knowledge_qa|data_analysis|document_analysis|general",
  "needs_retrieval": true|false,
  "needs_tools": true|false,
  "keywords": ["关键词1", "关键词2"]
}}

用户问题：{query}

只返回 JSON，不要其他内容。"""


async def analyze_query(state: AgentState, llm: LLMService | None = None) -> dict:
    """分析用户问题，返回状态更新。"""
    if llm is None:
        from app.services.dependencies import get_llm_service
        llm = get_llm_service()

    import json

    prompt = ANALYZE_PROMPT.format(query=state["query"])
    raw = await llm.generate(prompt)

    try:
        analysis = json.loads(raw)
    except json.JSONDecodeError:
        analysis = {
            "query_type": "knowledge_qa",
            "needs_retrieval": True,
            "needs_tools": False,
            "keywords": state["query"].split(),
        }

    # 确保必要字段存在
    analysis.setdefault("query_type", "knowledge_qa")
    analysis.setdefault("needs_retrieval", True)
    analysis.setdefault("needs_tools", False)
    analysis.setdefault("keywords", [])

    return {
        "query_analysis": analysis,
        "messages": [{"role": "query_analyzer", "content": str(analysis)}],
        "step_count": state["step_count"] + 1,
    }
