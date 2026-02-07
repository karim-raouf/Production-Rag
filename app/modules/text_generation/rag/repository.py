from loguru import logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import ScoredPoint
import uuid
from app.core.config import get_settings, AppSettings


class VectorRepository:
    def __init__(self, settings: AppSettings = None) -> None:
        self.settings = settings or get_settings()
        self.db_client = AsyncQdrantClient(
            host=self.settings.qdrant_host, port=self.settings.qdrant_port
        )

    async def create_collection(self, collection_name: str) -> bool:
        vector_config = models.VectorParams(
            size=self.settings.embed_size, distance=models.Distance.COSINE
        )

        if await self.db_client.collection_exists(collection_name):
            logger.debug(f"Collection {collection_name} already exists")
            return False

        logger.info(f"Creating collection {collection_name}")
        return await self.db_client.create_collection(
            collection_name=collection_name, vectors_config=vector_config
        )

    async def delete_collection(self, collection_name: str) -> bool:
        if not await self.db_client.collection_exists(collection_name):
            logger.debug(f"Collection {collection_name} does not exist")
            return False
        logger.info(f"Deleting collection {collection_name}")
        return await self.db_client.delete_collection(collection_name)

    async def create(
        self,
        collection_name: str,
        embedding_vector: list[float],
        original_text: str,
        source: str,
    ) -> None:
        if not await self.db_client.collection_exists(collection_name):
            raise ValueError(f"Collection {collection_name} does not exist")

        point_id = str(uuid.uuid4())

        logger.info(
            f"Adding document to collection {collection_name} with ID ({point_id})"
        )
        await self.db_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding_vector,
                    payload={"source": source, "original_text": original_text},
                )
            ],
        )

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        retrieval_limit: int,
        score_threshold: float,
    ) -> list[ScoredPoint]:
        if not await self.db_client.collection_exists(collection_name):
            raise ValueError(f"Collection {collection_name} does not exist")

        logger.debug(
            f"Searching for relevant items in the {collection_name} collection"
        )
        response = await self.db_client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=retrieval_limit,
            score_threshold=score_threshold,
        )

        return response.points


vector_repository = VectorRepository()
