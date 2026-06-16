import hashlib
import math
from typing import Iterable

import voyageai

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._client = voyageai.Client(api_key=settings.voyage_api_key) if settings.voyage_api_key else None
        self.vector_size = settings.qdrant_vector_size

    def _fallback_embedding(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode('utf-8')).digest()
        vals = [((digest[i % len(digest)] / 255.0) * 2.0) - 1.0 for i in range(self.vector_size)]
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        texts = list(texts)
        if not texts:
            return []
        if self._client:
            result = self._client.embed(texts, model=settings.voyage_embedding_model, input_type='document')
            return [list(v) for v in result.embeddings]
        return [self._fallback_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        if self._client:
            result = self._client.embed([text], model=settings.voyage_embedding_model, input_type='query')
            return list(result.embeddings[0])
        return self._fallback_embedding(text)
