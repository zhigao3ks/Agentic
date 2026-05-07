"""WebSocket 流式输出事件类型定义。"""

from enum import Enum

from pydantic import BaseModel, Field


class WSEventType(str, Enum):
    QUERY_ANALYZED = "query_analyzed"
    RETRIEVAL_STARTED = "retrieval_started"
    RETRIEVAL_COMPLETED = "retrieval_completed"
    MCP_TOOL_CALL = "mcp_tool_call"
    MCP_TOOL_RESULT = "mcp_tool_result"
    ANSWER_DELTA = "answer_delta"
    CITATION = "citation"
    ERROR = "error"
    DONE = "done"


class WSEvent(BaseModel):
    event: WSEventType
    data: dict | str = Field(default_factory=dict)


def query_analyzed(query_type: str, needs_tools: bool) -> WSEvent:
    return WSEvent(event=WSEventType.QUERY_ANALYZED, data={"query_type": query_type, "needs_tools": needs_tools})


def retrieval_started() -> WSEvent:
    return WSEvent(event=WSEventType.RETRIEVAL_STARTED, data="开始检索知识库")


def retrieval_completed(chunk_count: int) -> WSEvent:
    return WSEvent(event=WSEventType.RETRIEVAL_COMPLETED, data={"chunk_count": chunk_count})


def mcp_tool_call(tool_name: str, arguments: dict) -> WSEvent:
    return WSEvent(event=WSEventType.MCP_TOOL_CALL, data={"tool": tool_name, "arguments": arguments})


def mcp_tool_result(tool_name: str, is_error: bool) -> WSEvent:
    return WSEvent(event=WSEventType.MCP_TOOL_RESULT, data={"tool": tool_name, "is_error": is_error})


def answer_delta(delta: str) -> WSEvent:
    return WSEvent(event=WSEventType.ANSWER_DELTA, data=delta)


def citation_event(citations: list[dict]) -> WSEvent:
    return WSEvent(event=WSEventType.CITATION, data={"citations": citations})


def error_event(message: str) -> WSEvent:
    return WSEvent(event=WSEventType.ERROR, data=message)


def done_event(answer: str = "") -> WSEvent:
    return WSEvent(event=WSEventType.DONE, data="完成")
