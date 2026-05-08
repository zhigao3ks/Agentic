"""测试 Chart Generation MCP Server 工具。"""

import json

import pytest


@pytest.mark.asyncio
class TestBarChart:
    async def test_bar_chart_success(self):
        from app.mcp_servers.chart_generation.server import _bar_chart

        result = await _bar_chart({
            "data": {"Python": 85, "Java": 70, "JavaScript": 60},
            "title": "Languages",
        })
        data = json.loads(result[0].text)
        assert "base64" in data
        assert "data_uri" in data
        assert data["data_uri"].startswith("data:image/png;base64,")

    async def test_bar_chart_empty_data(self):
        from app.mcp_servers.chart_generation.server import _bar_chart

        result = await _bar_chart({"data": {}})
        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
class TestLineChart:
    async def test_line_chart_success(self):
        from app.mcp_servers.chart_generation.server import _line_chart

        result = await _line_chart({
            "x_labels": ["Q1", "Q2", "Q3", "Q4"],
            "series": {"Sales": [100, 200, 150, 300], "Profit": [20, 50, 30, 80]},
            "title": "Quarterly",
        })
        data = json.loads(result[0].text)
        assert "base64" in data

    async def test_line_chart_no_data(self):
        from app.mcp_servers.chart_generation.server import _line_chart

        result = await _line_chart({"x_labels": [], "series": {}})
        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
class TestTableSummary:
    async def test_table_summary(self):
        from app.mcp_servers.chart_generation.server import _table_summary

        result = await _table_summary({
            "headers": ["Name", "Age", "City"],
            "rows": [["Alice", "30", "NYC"], ["Bob", "25", "LA"]],
            "title": "Users",
        })
        data = json.loads(result[0].text)
        assert data["total_rows"] == 2
        assert "Alice" in data["table_text"]

    async def test_table_truncation(self):
        from app.mcp_servers.chart_generation.server import _table_summary

        rows = [[str(i), f"val{i}"] for i in range(100)]
        result = await _table_summary({
            "headers": ["ID", "Value"], "rows": rows, "max_rows": 10,
        })
        data = json.loads(result[0].text)
        assert data["displayed_rows"] == 10
        assert data["total_rows"] == 100


@pytest.mark.asyncio
class TestToolListing:
    async def test_list_tools(self):
        from app.mcp_servers.chart_generation.server import handle_list_tools

        tools = await handle_list_tools()
        assert len(tools) == 3
        names = [t.name for t in tools]
        assert "generate_bar_chart" in names
        assert "generate_line_chart" in names
        assert "generate_table_summary" in names


@pytest.mark.asyncio
class TestDispatch:
    async def test_dispatch_to_bar_chart(self):
        from app.mcp_servers.chart_generation.server import handle_call_tool

        result = await handle_call_tool("generate_bar_chart",
                                         {"data": {"A": 10, "B": 20}})
        data = json.loads(result[0].text)
        assert "base64" in data

    async def test_dispatch_unknown_tool(self):
        from app.mcp_servers.chart_generation.server import handle_call_tool

        result = await handle_call_tool("unknown_tool", {})
        data = json.loads(result[0].text)
        assert "error" in data
