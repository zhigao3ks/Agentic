"""测试 WebSocket 事件 Schema。"""

from app.schemas.ws_events import (
    WSEventType,
    answer_delta,
    citation_event,
    done_event,
    error_event,
    mcp_tool_call,
    mcp_tool_result,
    query_analyzed,
    retrieval_completed,
    retrieval_started,
)


class TestWSEvents:
    def test_query_analyzed_event(self):
        evt = query_analyzed("knowledge_qa", True)
        assert evt.event == WSEventType.QUERY_ANALYZED
        assert evt.data["query_type"] == "knowledge_qa"
        assert evt.data["needs_tools"] is True

    def test_retrieval_started_event(self):
        evt = retrieval_started()
        assert evt.event == WSEventType.RETRIEVAL_STARTED

    def test_retrieval_completed_event(self):
        evt = retrieval_completed(5)
        assert evt.event == WSEventType.RETRIEVAL_COMPLETED
        assert evt.data["chunk_count"] == 5

    def test_answer_delta_event(self):
        evt = answer_delta("你好")
        assert evt.event == WSEventType.ANSWER_DELTA
        assert evt.data == "你好"

    def test_citation_event(self):
        evt = citation_event([{"index": 1}])
        assert evt.event == WSEventType.CITATION
        assert len(evt.data["citations"]) == 1

    def test_mcp_tool_call_event(self):
        evt = mcp_tool_call("search", {"query": "test"})
        assert evt.event == WSEventType.MCP_TOOL_CALL
        assert evt.data["tool"] == "search"

    def test_mcp_tool_result_event(self):
        evt = mcp_tool_result("search", False)
        assert evt.event == WSEventType.MCP_TOOL_RESULT
        assert evt.data["is_error"] is False

    def test_error_event(self):
        evt = error_event("something went wrong")
        assert evt.event == WSEventType.ERROR

    def test_done_event(self):
        evt = done_event()
        assert evt.event == WSEventType.DONE

    def test_model_dump(self):
        evt = answer_delta("test")
        d = evt.model_dump()
        assert d == {"event": "answer_delta", "data": "test"}
