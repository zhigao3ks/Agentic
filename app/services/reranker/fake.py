"""Fake Reranker —— 用于测试，保持原顺序截断。"""

from app.services.reranker.base import RerankerService


class FakeReranker(RerankerService):
    async def rerank(self, query: str, chunks: list[dict], top_k: int = 8) -> list[dict]:
        return chunks[:top_k]
