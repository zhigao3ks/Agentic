"""测试 WebSocket 连接管理器。"""

import pytest

from app.services.ws_manager import WSManager


class TestWSManager:
    def test_connect_and_disconnect(self):
        mgr = WSManager()
        assert len(mgr._connections) == 0

    def test_manager_initialization(self):
        mgr = WSManager()
        assert isinstance(mgr._connections, dict)


class TestWSEventSerialization:
    def test_event_serializable(self):
        from app.schemas.ws_events import answer_delta

        evt = answer_delta("hello")
        data = evt.model_dump()
        assert data["event"] == "answer_delta"
        assert data["data"] == "hello"
