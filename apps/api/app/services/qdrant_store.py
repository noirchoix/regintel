from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from app.core.config import settings


class QdrantStore:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=30)
        self.collection = settings.qdrant_collection

    def ensure_collection(self) -> None:
        collections = {c.name for c in self.client.get_collections().collections}
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=settings.qdrant_vector_size, distance=Distance.COSINE),
            )
            for field in ['jurisdiction', 'framework', 'document_id', 'version']:
                self.client.create_payload_index(self.collection, field_name=field, field_schema='keyword')

    def upsert_chunks(self, chunks: list[dict[str, Any]]) -> None:
        points = [PointStruct(id=str(uuid4()), vector=chunk['vector'], payload=chunk['payload']) for chunk in chunks]
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: list[float], *, jurisdiction: str | None = None, frameworks: list[str] | None = None, limit: int = 8):
        conditions = []
        if jurisdiction:
            conditions.append(FieldCondition(key='jurisdiction', match=MatchValue(value=jurisdiction)))
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            query_filter=Filter(must=conditions) if conditions else None,
            limit=limit * 3,
            with_payload=True,
        )
        if frameworks:
            allowed = set(frameworks)
            hits = [h for h in hits if h.payload.get('framework') in allowed]
        return hits[:limit]
