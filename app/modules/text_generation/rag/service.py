from loguru import logger
from .repository import VectorRepository
from .transform import clean, embed, load


class VectorService(VectorRepository):
    def __init__(self):
        super().__init__()

    async def store_file_content_in_db(
        self,
        filepath: str,
        collection_name: str,
    ) -> None:
        await self.create_collection(collection_name=collection_name)
        logger.debug(f"Processing file {filepath}")

        async for chunk in load(filepath, self.settings):
            cleaned_chunk = clean(chunk)
            embedded_chunk = embed(cleaned_chunk)
            logger.debug(f"Embedding chunk {cleaned_chunk[:20]}")

            await self.create(
                collection_name=collection_name,
                embedding_vector=embedded_chunk,
                original_text=cleaned_chunk,
                source=filepath,
            )


vector_service = VectorService()
