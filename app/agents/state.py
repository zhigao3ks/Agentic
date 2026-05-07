"""Agent 状态定义。"""

import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    query: str
    kb_id: str
    session_id: str | None
    messages: Annotated[list[dict], operator.add]
    query_analysis: dict
    retrieved_chunks: list[dict]
    answer: str
    citations: list[dict]
    verification: dict
    status: str
    step_count: int
    max_steps: int
    error: str | None


def make_initial_state(query: str, kb_id: str, session_id: str | None = None) -> AgentState:
    return AgentState(
        query=query,
        kb_id=kb_id,
        session_id=session_id,
        messages=[],
        query_analysis={},
        retrieved_chunks=[],
        answer="",
        citations=[],
        verification={},
        status="running",
        step_count=0,
        max_steps=10,
        error=None,
    )
