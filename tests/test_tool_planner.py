"""测试 Tool Planner Agent。"""

import pytest

from app.agents.state import make_initial_state


@pytest.mark.asyncio
class TestToolPlanner:
    async def test_no_tools_needed(self):
        from app.agents.tool_planner import plan_tools

        state = make_initial_state("什么是 Python？", "kb1")
        state["query_analysis"] = {"needs_tools": False}

        result = await plan_tools(state)
        assert result["tool_calls"] == []

    async def test_plans_tools_when_needed(self):
        from app.agents.tool_planner import plan_tools

        state = make_initial_state("查询数据库中的用户数量", "kb1")
        state["query_analysis"] = {
            "needs_tools": True,
            "query_type": "data_analysis",
            "keywords": ["用户", "数量"],
        }

        result = await plan_tools(state)
        assert "tool_calls" in result
        assert "messages" in result
