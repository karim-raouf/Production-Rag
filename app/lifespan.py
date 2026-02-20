from app.modules.text_generation.infrastructure.model_lifecycle import (
    load_models_at_startup,
    clear_models_at_shutdown,
)
from app.core.logging import setup_logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis
from .core.api_limiters import init_limiters


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = Redis.from_url("redis://localhost:6379", decode_responses=True)
    await init_limiters(redis_client)
    setup_logging()
    load_models_at_startup()

    yield

    await redis_client.aclose()
    clear_models_at_shutdown()