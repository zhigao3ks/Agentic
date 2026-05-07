"""Embedding 服务抽象接口。"""

from abc import ABC, abstractmethod


class EmbeddingService(ABC):
    """Embedding 服务抽象基类。"""

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量文本向量化。"""
        ...

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """单条查询文本向量化。"""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """向量维度。"""
        ...
