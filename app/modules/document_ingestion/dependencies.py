from fastapi import Response
from ...core import api_limiters
from app.core.api_limiters import get_user_id
from fastapi_limiter.depends import RateLimiter
from fastapi import Request
from loguru import logger

#-----------------------API LIMITS-----------------------------------------------

async def limit_docs_ingestion(request: Request, response: Response):
    if api_limiters.docs_limiter:
        await RateLimiter(limiter=api_limiters.docs_limiter, identifier=get_user_id)(
            request, response
        )
    else:
        logger.warning("Docs limiter not initialized")