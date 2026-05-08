"""Chart Generation MCP Server —— 提供 3 个工具：柱状图、折线图、表格摘要。

启动方式：python -m app.mcp_servers.chart_generation.server
"""

import asyncio
import base64
import io
import json
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("chart-generation-mcp")

OUTPUT_DIR = os.environ.get("CHART_OUTPUT_DIR", "./storage/charts")


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate_bar_chart",
            description="生成柱状图，返回 PNG 图片的 base64 编码和文件路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": '标签到数值的映射，如 {"Python": 85, "Java": 70, "JavaScript": 60}',
                    },
                    "title": {"type": "string", "description": "图表标题", "default": "Bar Chart"},
                    "x_label": {"type": "string", "description": "X 轴标签", "default": ""},
                    "y_label": {"type": "string", "description": "Y 轴标签", "default": ""},
                },
                "required": ["data"],
            },
        ),
        Tool(
            name="generate_line_chart",
            description="生成折线图，支持多条折线，返回 PNG 图片的 base64 编码和文件路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "x_labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "X 轴标签列表",
                    },
                    "series": {
                        "type": "object",
                        "description": '系列名到数值列表的映射，如 {"销售额": [100,200,300], "利润": [20,50,80]}',
                    },
                    "title": {"type": "string", "description": "图表标题", "default": "Line Chart"},
                    "x_label": {"type": "string", "description": "X 轴标签", "default": ""},
                    "y_label": {"type": "string", "description": "Y 轴标签", "default": ""},
                },
                "required": ["x_labels", "series"],
            },
        ),
        Tool(
            name="generate_table_summary",
            description="生成格式化表格文本摘要，支持排序和截断",
            inputSchema={
                "type": "object",
                "properties": {
                    "headers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "表头列表",
                    },
                    "rows": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}},
                        "description": "表格数据行",
                    },
                    "title": {"type": "string", "description": "表格标题", "default": "Table"},
                    "max_rows": {"type": "integer", "description": "最大显示行数", "default": 50},
                },
                "required": ["headers", "rows"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "generate_bar_chart":
        return await _bar_chart(arguments)
    elif name == "generate_line_chart":
        return await _line_chart(arguments)
    elif name == "generate_table_summary":
        return await _table_summary(arguments)
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False))]


async def _bar_chart(args: dict) -> list[TextContent]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = args.get("data", {})
    title = args.get("title", "Bar Chart")
    x_label = args.get("x_label", "")
    y_label = args.get("y_label", "")

    if not data or not isinstance(data, dict):
        return [TextContent(type="text", text=json.dumps({"error": "data must be a non-empty dict"}, ensure_ascii=False))]

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis([i / len(labels) for i in range(len(labels))])
    ax.bar(labels, values, color=colors, edgecolor="white")
    ax.set_title(title, fontsize=14, fontweight="bold")
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()

    result = _fig_to_result(fig, title)
    plt.close(fig)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]


async def _line_chart(args: dict) -> list[TextContent]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x_labels = args.get("x_labels", [])
    series = args.get("series", {})
    title = args.get("title", "Line Chart")
    x_label = args.get("x_label", "")
    y_label = args.get("y_label", "")

    if not x_labels or not series:
        return [TextContent(type="text", text=json.dumps({"error": "x_labels and series are required"}, ensure_ascii=False))]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(x_labels))
    for name, values in series.items():
        if len(values) == len(x_labels):
            ax.plot(x, values, marker="o", linewidth=2, label=name)

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=30)
    ax.set_title(title, fontsize=14, fontweight="bold")
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    result = _fig_to_result(fig, title)
    plt.close(fig)
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]


async def _table_summary(args: dict) -> list[TextContent]:
    headers = args.get("headers", [])
    rows = args.get("rows", [])
    title = args.get("title", "Table")
    max_rows = min(args.get("max_rows", 50), 200)

    if not headers:
        return [TextContent(type="text", text=json.dumps({"error": "headers is required"}, ensure_ascii=False))]

    truncated = len(rows) > max_rows
    display_rows = rows[:max_rows]

    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in display_rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # 构建表格
    def _fmt_row(cells):
        return "| " + " | ".join(str(c).ljust(col_widths[i]) if i < len(col_widths) else str(c)
                                  for i, c in enumerate(cells)) + " |"

    separator = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"
    lines = [f"## {title}", "", _fmt_row(headers), separator]
    for row in display_rows:
        lines.append(_fmt_row(row))

    if truncated:
        lines.append(f"\n*(共 {len(rows)} 行，显示前 {max_rows} 行)*")

    return [TextContent(type="text", text=json.dumps({
        "table_text": "\n".join(lines),
        "total_rows": len(rows),
        "displayed_rows": len(display_rows),
    }, ensure_ascii=False))]


def _fig_to_result(fig, title: str) -> dict:
    """将 matplotlib figure 转为 base64 PNG + 保存到文件。"""
    _ensure_output_dir()
    safe_name = title.replace(" ", "_").replace("/", "_")[:50]
    file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.png")
    fig.savefig(file_path, dpi=100, bbox_inches="tight")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")

    return {
        "base64": b64,
        "file_path": file_path,
        "format": "png",
        "data_uri": f"data:image/png;base64,{b64}",
    }


def main():
    async def _run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
