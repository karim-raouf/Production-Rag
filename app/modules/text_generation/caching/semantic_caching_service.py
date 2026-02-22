from .caching_client import CacheClient
from ..rag.transform import embed


class SemanticCacheService(CacheClient):
    def __init__(self):
        super().__init__()

    async def cache_check(self, user_query: str):
        query_embedding = embed(user_query)

        if response_cache := await self.search_response_cache(
            query_vector=query_embedding
        ):
            return ("response", response_cache, query_embedding)

        if doc_cache := await self.search_doc_cache(query_vector=query_embedding):
            return ("documents", doc_cache, query_embedding)

        else:
            return (None, None, query_embedding)


semantic_cache_service = SemanticCacheService()
