from .service import vector_service
from .transform import embed
from loguru import logger
from ..schemas import TextToTextRequest
from fastapi import Body


async def fetch_rag_content(prompt: str):
    try:
        rag_content = await vector_service.search(
            collection_name="KnowledgeBase",
            query_vector=embed(prompt),
            retrieval_limit=3,
            score_threshold=0.1,
        )

        rag_content_str = "\n".join([c.payload["original_text"] for c in rag_content])

        return rag_content_str
    except Exception as e:
        logger.warning(f"Failed to fetch RAG content: {e}")
        return None


async def get_rag_content(body: TextToTextRequest = Body(...)):
    return await fetch_rag_content(body.prompt)
