from .service import vector_service
from .transform import embed
from loguru import logger
from ..schemas import TextToTextRequest
from fastapi import Body
import asyncio


# for streaming as sse uses get request and cant have body in get request
async def fetch_rag_content(query_str_or_vector: str | list[float]) -> str | None:
    embedding = None
    try:
        if query_str_or_vector:
            if isinstance(query_str_or_vector, str):
                embedding = await asyncio.to_thread(embed, query_str_or_vector)
            else:
                embedding = query_str_or_vector

            rag_content = await vector_service.search(
                collection_name="KnowledgeBase",
                query_vector=embedding,
                retrieval_limit=4,
                score_threshold=0.4,
            )

            rag_content_str = "\n".join([c.payload.get("original_text", "") for c in rag_content])

            return rag_content_str

        return None

    except Exception as e:
        logger.warning(f"Failed to fetch RAG content: {e}")
        return None


async def get_rag_content(body: TextToTextRequest = Body(...)):
    return await fetch_rag_content(body.prompt)
