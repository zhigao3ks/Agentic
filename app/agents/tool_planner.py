"""Tool Planner Agent —— 根据问题分析结果规划需要调用的 MCP 工具及参数。"""

import json

from app.agents.state import AgentState
from app.services.llm.base import LLMService

PLAN_PROMPT = """你是一个工具规划助手。根据用户问题分析结果，决定需要调用哪些 MCP 工具。

可用工具：
- search_knowledge_base(query, kb_id, top_k): 知识库检索
- execute_readonly_sql(sql_query, limit): 执行只读 SQL 查询
- list_tables(): 列出数据库表名
- describe_table(table_name): 获取表结构

用户问题：{query}
问题分析：{analysis}

请返回 JSON 格式的工具调用计划：
[{{
  "tool": "工具名",
  "arguments": {{"参数名": "参数值"}}
}}]

如果不需要工具调用，返回空数组 []。
只返回 JSON，不要其他内容。"""


async def plan_tools(state: AgentState, llm: LLMService | None = None) -> dict:
    """分析问题并规划工具调用。"""
    if llm is None:
        from app.services.dependencies import get_llm_service
        llm = get_llm_service()

    analysis = state.get("query_analysis", {})
    if not analysis.get("needs_tools"):
        return {
            "tool_calls": [],
            "messages": [{"role": "tool_planner", "content": "no tools needed"}],
            "step_count": state["step_count"] + 1,
        }

    prompt = PLAN_PROMPT.format(query=state["query"], analysis=json.dumps(analysis, ensure_ascii=False))
    raw = await llm.generate(prompt)

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        plan = []

    if not isinstance(plan, list):
        plan = []

    return {
        "tool_calls": plan,
        "messages": [{"role": "tool_planner", "content": str(plan)}],
        "step_count": state["step_count"] + 1,
    }
