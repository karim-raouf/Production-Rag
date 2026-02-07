import asyncio
import platform
from fastapi import FastAPI, Request

# Fix for asyncpg on Windows
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from contextlib import asynccontextmanager
import time
from uuid import uuid4
from starlette.background import BackgroundTask
from datetime import datetime, timezone
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.ml import global_ml_store
from app.core.logging import write_log_to_csv, setup_logging
from app.modules.text_generation.router import router as text_gen_router
from app.modules.document_ingestion.router import router as doc_ingestion_router
from app.core.database.routers import conversations_router, messages_router
from app.modules.text_generation.infrastructure.model_lifecycle import (
    load_models_at_startup,
    clear_models_at_shutdown,
)
from .basic_auth import AuthenticatedUserDep

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    load_models_at_startup()

    yield

    clear_models_at_shutdown()


app = FastAPI(lifespan=lifespan)

# CORS Middleware - must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def monitor_service(request: Request, call_next):
    # Skip monitoring for streaming endpoints to avoid buffering
    # if "/stream/" in request.url.path:
    #     return await call_next(request)

    request_id = uuid4().hex
    request_datetime = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = round(time.perf_counter() - start_time, 4)
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Request-ID"] = request_id

    log_data = [
        request_id,
        request_datetime,
        str(request.url),
        request.client.host,
        process_time,
        response.status_code,
        response.status_code < 400,
    ]

    log_task = BackgroundTask(write_log_to_csv, log_data)

    if response.background:
        old_bg = response.background

        async def combined_bg():
            await old_bg()
            await log_task()

        response.background = BackgroundTask(combined_bg)
    else:
        response.background = log_task

    return response


# Serving static files
app.mount("/pages", StaticFiles(directory="app/pages"), name="pages")


# Modules Endpoints

app.include_router(text_gen_router)
app.include_router(doc_ingestion_router)
app.include_router(conversations_router)
app.include_router(messages_router)

# Health Check


@app.get("/api/health")
def health_check(username: AuthenticatedUserDep):
    return {
        "status": "ok",
        "model_loaded": global_ml_store.get("embed_model") is not None,
        "username" : username
    }
