"""测试 Agent 状态定义。"""

from app.agents.state import AgentState, make_initial_state


class TestAgentState:
    def test_make_initial_state(self):
        state = make_initial_state("test query", "test-kb-id")
        assert state["query"] == "test query"
        assert state["kb_id"] == "test-kb-id"
        assert state["status"] == "running"
        assert state["step_count"] == 0
        assert state["messages"] == []
        assert state["retrieved_chunks"] == []

    def test_messages_accumulate(self):
        """验证 Annotated[list, operator.add] 使消息累加。"""
        s1 = make_initial_state("q", "kb1")
        s2 = AgentState(
            query="q", kb_id="kb1", session_id=None, messages=[{"role": "test", "content": "hello"}],
            query_analysis={}, retrieved_chunks=[], answer="", citations=[],
            verification={}, status="running", step_count=0, max_steps=10, error=None,
        )
        assert len(s2["messages"]) == 1
