"""Chroma 向量数据库实现。"""

import asyncio

import chromadb

from app.core.config import settings
from app.services.vector_store.base import VectorStore


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_dir: str | None = None) -> None:
        self._client = chromadb.PersistentClient(
            path=persist_dir or settings.CHROMA_PERSIST_DIR
        )

    def _get_collection(self, kb_id: str):
        return self._client.get_or_create_collection(name=f"kb_{kb_id}")

    async def add_vectors(
        self, ids: list[str], vectors: list[list[float]], metadatas: list[dict]
    ) -> None:
        # ChromaDB 的 add 是同步的，放在线程池中执行
        loop = asyncio.get_running_loop()

        # 从第一个 metadata 推断 kb_id
        kb_id = metadatas[0].get("kb_id", "default") if metadatas else "default"
        collection = self._get_collection(kb_id)

        await loop.run_in_executor(
            None,
            lambda: collection.add(ids=ids, embeddings=vectors, metadatas=metadatas),
        )

    async def search(
        self, query_vector: list[float], top_k: int = 10, filter_dict: dict | None = None
    ) -> list[dict]:
        loop = asyncio.get_running_loop()

        # 从 filter 推断 kb_id
        kb_id = (filter_dict or {}).get("kb_id", "default")
        collection = self._get_collection(kb_id)
        where = {k: v for k, v in (filter_dict or {}).items() if k != "kb_id"} or None

        results = await loop.run_in_executor(
            None,
            lambda: collection.query(
                query_embeddings=[query_vector], n_results=top_k, where=where
            ),
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        return [
            {
                "id": results["ids"][0][i],
                "score": 1 - (results["distances"][0][i] if results["distances"] else 0),
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            }
            for i in range(len(results["ids"][0]))
        ]

    async def delete(self, ids: list[str]) -> None:
        loop = asyncio.get_running_loop()
        # 遍历所有 collection 来删除（Chroma 的限制）
        collections = self._client.list_collections()
        for col in collections:
            await loop.run_in_executor(None, lambda c=col: c.delete(ids=ids))

    async def delete_by_filter(self, filter_dict: dict) -> None:
        kb_id = filter_dict.get("kb_id", "default")
        collection = self._get_collection(kb_id)
        where = {k: v for k, v in filter_dict.items() if k != "kb_id"} or None
        loop = asyncio.get_running_loop()

        if where:
            results = collection.get(where=where)
            if results["ids"]:
                await loop.run_in_executor(None, lambda: collection.delete(ids=results["ids"]))
        else:
            await loop.run_in_executor(None, lambda: self._client.delete_collection(f"kb_{kb_id}"))
