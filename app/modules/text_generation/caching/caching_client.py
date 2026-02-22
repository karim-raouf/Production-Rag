import uuid
from datetime import datetime, timezone
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.http.models import Distance, PointStruct
from app.core.config import get_settings


class CacheClient:
    def __init__(self) -> None:
        self.setting = get_settings()
        self.doc_cache_collection = "doc_cache"
        self.response_cache_collection = "response_cache"
        self.caching_db_client = AsyncQdrantClient(
            host=self.setting.qdrant_caching_host, port=self.setting.qdrant_caching_port
        )

    async def init_caching_db(self) -> None:
        vector_config = models.VectorParams(
            size=self.setting.embed_size, distance=Distance.COSINE
        )

        await self.caching_db_client.recreate_collection(
            collection_name=self.doc_cache_collection, vectors_config=vector_config
        )

        await self.caching_db_client.recreate_collection(
            collection_name=self.response_cache_collection, vectors_config=vector_config
        )

    async def insert_doc_cache(
        self, query_vector: list[float], documents: list[str]
    ) -> None:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=query_vector,
            payload={
                "documents": documents,
                "created_at": datetime.now(timezone.utc).timestamp(),
            },
        )

        await self.caching_db_client.upsert(
            collection_name=self.doc_cache_collection, points=[point]
        )

    async def insert_response_cache(
        self, query_vector: list[float], response: str
    ) -> None:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=query_vector,
            payload={
                "response": response,
                "created_at": datetime.now(timezone.utc).timestamp(),
            },
        )

        await self.caching_db_client.upsert(
            collection_name=self.response_cache_collection, points=[point]
        )

    async def search_doc_cache(self, query_vector: list[float]) -> str | None:
        result = await self.caching_db_client.query_points(
            collection_name=self.doc_cache_collection,
            query=query_vector,
            limit=1,
            score_threshold=0.95,
        )
        if result.points:
            return result.points[0].payload["documents"]

        return None

    async def search_response_cache(self, query_vector: list[float]) -> str | None:
        result = await self.caching_db_client.query_points(
            collection_name=self.response_cache_collection,
            query=query_vector,
            limit=1,
            score_threshold=0.98,
        )
        if result.points:
            return result.points[0].payload["response"]

        return None

    async def delete_expired(self, ttl_seconds: int = 86400) -> None:
        """
        Deletes points older than the TTL (default 24 hours).
        """
        expiration_time = datetime.now(timezone.utc).timestamp() - ttl_seconds

        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="created_at",
                    range=models.Range(lt=expiration_time),
                )
            ]
        )

        await self.caching_db_client.delete(
            collection_name=self.doc_cache_collection, points_selector=filter_condition
        )

        await self.caching_db_client.delete(
            collection_name=self.response_cache_collection,
            points_selector=filter_condition,
        )
