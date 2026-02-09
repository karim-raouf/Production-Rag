from fastapi import APIRouter, Request, Body, Depends, Query
from fastapi.responses import StreamingResponse
from .schemas import TextToTextRequest, TextToTextResponse
from .services.generation_service import generate_text
from .services.ollama_cloud_service import OllamaCloudChatClient
from .dependencies import get_ollama_client
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
from ...core.database.dependencies import DBSessionDep
from ...core.database.repositories import MessageRepository
from ...core.database.schemas import MessageCreate
from ...core.database.routers.conversations.dependencies import GetConversationDep


from typing import AsyncGenerator

# from app.core.ml import global_ml_store
from .scraping.dependencies import get_urls_content, fetch_urls_content
from .rag.dependencies import get_rag_content, fetch_rag_content
from app.core.config import AppSettings, get_settings
from app.modules.text_generation.services.stream import ws_manager
from loguru import logger
import re

router = APIRouter(
    prefix="/text-generation",
    tags=["Text Generation"],
)


@router.post("/text-to-text", response_model=TextToTextResponse)
async def text_to_text(
    request: Request,
    body: TextToTextRequest = Body(...),
    urls_content=Depends(get_urls_content),
    rag_content=Depends(get_rag_content),
    settings: AppSettings = Depends(get_settings),
):
    logger.info(f"Received Body Prompt: {body.prompt}")
    logger.info(f"Received URLs Content: {urls_content}")
    logger.info(f"Received RAG Content: {rag_content}")

    if not body.prompt:
        logger.warning("No prompt provided")

    if urls_content is None:
        logger.warning("No urls content provided")

    if rag_content is None:
        logger.warning("No rag content provided")

    prompt_parts = [
        body.prompt,
        urls_content
        if urls_content is not None
        else "urls content Couldn't be fetched",
        rag_content if rag_content is not None else "rag content Couldn't be fetched",
    ]
    prompt = "\n\n".join(prompt_parts)

    result = await generate_text(
        prompt, temperature=0.7, vllm_api_key=settings.vllm_api_key
    )  # global_ml_store.get(body.model)
    return TextToTextResponse(result=result)


@router.get("/stream/text-to-text/{conversation_id}")
async def stream_text_to_text(
    conversation: GetConversationDep,
    session: DBSessionDep,
    prompt: str = Query(...),
    client: OllamaCloudChatClient = Depends(get_ollama_client),
) -> StreamingResponse:
    # Manually fetch content using extracted service functions
    urls_content = await fetch_urls_content(prompt)
    rag_content = await fetch_rag_content(prompt)

    if not prompt:
        logger.warning("No prompt provided")
    else:
        logger.info("prompt provided")
    if urls_content is None:
        logger.warning("No urls content provided")
    else:
        logger.info("url content provided")
    if rag_content is None:
        logger.warning("No rag content provided")
    else:
        logger.info("rag content provided")

    prompt_parts = [
        prompt,
        urls_content
        if urls_content is not None
        else "urls content Couldn't be fetched",
        rag_content if rag_content is not None else "rag content Couldn't be fetched",
    ]
    full_prompt = "\n\n".join(prompt_parts)

    response_stream = client.stream_chat(
        prompt=full_prompt, model="qwen3-vl:235b-instruct-cloud"
    )

    async def stream_with_storage(
        stream: AsyncGenerator[str, None],
    ) -> AsyncGenerator[str, None]:
        stream_buffer = []
        try:
            async for chunk in stream:
                stream_buffer.append(chunk)
                yield chunk
        finally:
            final_response = "".join(stream_buffer)

            final_response = re.sub(r"data: |\n\n|\[DONE\]", "", final_response)
            
            await MessageRepository(session).create(
                MessageCreate.model_construct(
                    url_content=urls_content,
                    rag_content=rag_content,
                    request_content=prompt,
                    response_content=final_response,
                    conversation_id=conversation.id,
                )
            )

    return StreamingResponse(
        stream_with_storage(response_stream),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.websocket("/ws/text-to-text")
async def ws_text_to_text(
    ws: WebSocket,
    client: OllamaCloudChatClient = Depends(get_ollama_client),
):
    logger.info("Connecting to client....")
    await ws_manager.connect(ws)
    try:
        while True:
            prompt = await ws_manager.receive(ws)
            # Manually fetch content using extracted service functions
            urls_content = await fetch_urls_content(prompt)
            rag_content = await fetch_rag_content(prompt)
            logger.info(f"Received Body Prompt: {prompt}")
            logger.info(f"Received URLs Content: {urls_content}")
            logger.info(f"Received RAG Content: {rag_content}")

            if not prompt:
                logger.warning("No prompt provided")
            if urls_content is None:
                logger.warning("No urls content provided")
            if rag_content is None:
                logger.warning("No rag content provided")

            prompt_parts = [
                prompt,
                urls_content
                if urls_content is not None
                else "urls content Couldn't be fetched",
                rag_content
                if rag_content is not None
                else "rag content Couldn't be fetched",
            ]
            prompt = "\n\n".join(prompt_parts)

            async for chunk in client.stream_chat(
                prompt=prompt, model="qwen3-vl:235b-instruct-cloud", stream_mode="ws"
            ):
                await ws_manager.send(ws, chunk)
                await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await ws_manager.send(ws, f"an internal error occured!")
    finally:
        await ws_manager.disconnect(ws)
