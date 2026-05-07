"""MCP Tool Agent —— 统一执行 MCP 工具调用，处理结果和错误。"""

import time

from app.agents.state import AgentState
from app.core.logging import get_logger
from app.mcp_client.tool_caller import call_tool

logger = get_logger(__name__)

# 工具→MCP Server 映射
TOOL_SERVER_MAP = {
    "search_knowledge_base": "knowledge-base-mcp",
    "get_document_detail": "knowledge-base-mcp",
    "get_chunk_context": "knowledge-base-mcp",
    "list_tables": "sql-query-mcp",
    "describe_table": "sql-query-mcp",
    "execute_readonly_sql": "sql-query-mcp",
    "list_files": "file-system-mcp",
    "read_file": "file-system-mcp",
}


async def execute_tools(state: AgentState) -> dict:
    """执行规划好的 MCP 工具调用。"""
    tool_calls = state.get("tool_calls", [])

    if not tool_calls:
        return {
            "tool_results": [],
            "messages": [{"role": "mcp_tool_agent", "content": "no tools to execute"}],
            "step_count": state["step_count"] + 1,
        }

    results = []
    for tc in tool_calls:
        tool_name = tc.get("tool", "")
        arguments = tc.get("arguments", {})
        server_name = TOOL_SERVER_MAP.get(tool_name, "knowledge-base-mcp")

        # 补充 kb_id（如果工具需要但未提供）
        if "kb_id" in arguments and not arguments["kb_id"]:
            arguments["kb_id"] = state.get("kb_id", "")

        start = time.monotonic()
        try:
            result = await call_tool(server_name, tool_name, arguments)
            latency = int((time.monotonic() - start) * 1000)
            results.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result,
                "is_error": result.get("is_error", False),
                "latency_ms": latency,
            })
            logger.info("mcp_tool_executed", tool=tool_name, latency_ms=latency, error=result.get("is_error"))
        except Exception as e:
            results.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": {"is_error": True, "error": str(e)},
                "is_error": True,
                "latency_ms": 0,
            })
            logger.warning("mcp_tool_failed", tool=tool_name, error=str(e))

    return {
        "tool_results": results,
        "messages": [{"role": "mcp_tool_agent", "content": f"executed {len(results)} tool(s)"}],
        "step_count": state["step_count"] + 1,
    }
