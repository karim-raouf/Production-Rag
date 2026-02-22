import asyncio
from app.modules.text_generation.infrastructure.model_lifecycle import (
    load_models_at_startup,
    clear_models_at_shutdown,
)
from app.core.logging import setup_logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis
from .core.api_limiters import init_limiters
from .modules.text_generation.caching.caching_client import CacheClient


async def run_cache_eviction():
    client = CacheClient()
    while True:
        try:
            await client.delete_expired(
                ttl_seconds=86400
            )  # Evict items older than 24 hours
        except Exception:
            # Handle potential Qdrant connection errors gracefully
            pass

        # Sleep for an hour before checking again
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = Redis.from_url("redis://localhost:6379", decode_responses=True)
    await init_limiters(redis_client)
    await CacheClient().init_caching_db()
    setup_logging()
    load_models_at_startup()

    # Start the background eviction task
    eviction_task = asyncio.create_task(run_cache_eviction())

    yield

    # Cancel eviction task on shutdown
    eviction_task.cancel()
    try:
        await eviction_task
    except asyncio.CancelledError:
        pass

    await redis_client.aclose()
    clear_models_at_shutdown()
