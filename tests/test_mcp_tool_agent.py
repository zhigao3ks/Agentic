"""测试 MCP Tool Agent。"""

import pytest

from app.agents.state import make_initial_state


@pytest.mark.asyncio
class TestMCPToolAgent:
    async def test_no_tools_to_execute(self):
        from app.agents.mcp_tool_agent import execute_tools

        state = make_initial_state("test", "kb1")
        result = await execute_tools(state)
        assert result["tool_results"] == []

    async def test_executes_tool_calls(self):
        from app.agents.mcp_tool_agent import execute_tools

        state = make_initial_state("query", "kb1")
        state["tool_calls"] = [
            {"tool": "search_knowledge_base", "arguments": {"query": "test", "kb_id": "kb1"}},
        ]

        result = await execute_tools(state)
        assert "tool_results" in result
        # 没有真实 MCP server 运行时会返回 error，但不应抛出异常
        assert len(result["tool_results"]) >= 1

    async def test_multiple_tools(self):
        from app.agents.mcp_tool_agent import execute_tools

        state = make_initial_state("query", "kb1")
        state["tool_calls"] = [
            {"tool": "search_knowledge_base", "arguments": {"query": "a", "kb_id": "kb1"}},
            {"tool": "search_knowledge_base", "arguments": {"query": "b", "kb_id": "kb1"}},
        ]

        result = await execute_tools(state)
        assert len(result["tool_results"]) == 2

    async def test_unknown_tool_handled(self):
        from app.agents.mcp_tool_agent import execute_tools

        state = make_initial_state("query", "kb1")
        state["tool_calls"] = [{"tool": "nonexistent_tool", "arguments": {}}]

        result = await execute_tools(state)
        assert result["tool_results"][0]["is_error"] is True
