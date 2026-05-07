"""向量数据库抽象接口。"""

from abc import ABC, abstractmethod


class VectorStore(ABC):
    """向量存储抽象基类。"""

    @abstractmethod
    async def add_vectors(
        self, ids: list[str], vectors: list[list[float]], metadatas: list[dict]
    ) -> None:
        """批量添加向量及元数据。"""
        ...

    @abstractmethod
    async def search(
        self, query_vector: list[float], top_k: int = 10, filter_dict: dict | None = None
    ) -> list[dict]:
        """向量检索，返回 [{id, score, metadata}, ...]。"""
        ...

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        """按 ID 删除向量。"""
        ...

    @abstractmethod
    async def delete_by_filter(self, filter_dict: dict) -> None:
        """按条件删除向量。"""
        ...
