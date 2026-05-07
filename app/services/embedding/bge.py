"""BGE-M3 Embedding 服务 —— 通过 OpenAI-compatible API 调用。"""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.embedding.base import EmbeddingService


class BGEEmbeddingService(EmbeddingService):
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.EMBEDDING_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.EMBEDDING_API_KEY
        self.model = model or settings.EMBEDDING_MODEL
        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise RuntimeError("Dimension unknown; call embed_texts or embed_query first")
        return self._dimension

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await self._call_api(texts)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def embed_query(self, text: str) -> list[float]:
        results = await self._call_api([text])
        return results[0]

    async def _call_api(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                json={"model": self.model, "input": texts},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings = [item["embedding"] for item in data["data"]]
            self._dimension = len(embeddings[0])
            return embeddings
