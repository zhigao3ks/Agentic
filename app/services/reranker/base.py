"""Reranker 服务抽象接口。"""

from abc import ABC, abstractmethod


class RerankerService(ABC):
    """Reranker 抽象基类。"""

    @abstractmethod
    async def rerank(self, query: str, chunks: list[dict], top_k: int = 8) -> list[dict]:
        """对候选 chunk 进行精排，返回排序后的 TopK chunk。"""
        ...
