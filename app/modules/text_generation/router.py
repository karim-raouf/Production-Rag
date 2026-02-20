from fastapi import APIRouter, Request, Body, Depends, Query
from fastapi.responses import StreamingResponse
from .schemas import TextToTextRequest, TextToTextResponse
from .services.generation_service import generate_text
from .dependencies import OllamaClientDep, InputGuardrailDep, OutputGuardrailDep
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
from loguru import logger
from ...core.database.dependencies import DBSessionDep
from ...core.database.repositories import MessageRepository
from ...core.database.schemas import MessageCreate
from ...core.database.routers.conversations.dependencies import GetConversationDep
from .dependencies import limit_text_gen

from typing import AsyncGenerator

# from app.core.ml import global_ml_store
from .scraping.dependencies import get_urls_content, fetch_urls_content
from .rag.dependencies import get_rag_content, fetch_rag_content
from app.core.config import AppSettings, get_settings
from app.modules.text_generation.services.stream import ws_manager



router = APIRouter(
    prefix="/text-generation",
    tags=["Text Generation"],
    dependencies=[Depends(limit_text_gen)],
)


@router.post("/text-to-text/vllm", response_model=TextToTextResponse)
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


@router.post(
    "/text-to-text/ollama/{conversation_id}", response_model=TextToTextResponse
)
async def ollama_text_to_text(
    conversation: GetConversationDep,
    session: DBSessionDep,
    client: OllamaClientDep,
    input_guardrail: InputGuardrailDep,
    output_guardrail: OutputGuardrailDep,
    body: TextToTextRequest = Body(...),
):
    # Manually fetch content using extracted service functions
    input_guard_task = asyncio.create_task(
        input_guardrail.is_input_allowed(body.prompt)
    )
    urls_content_task = asyncio.create_task(fetch_urls_content(body.prompt))
    rag_content_task = asyncio.create_task(fetch_rag_content(body.prompt))

    input_guard_result = await input_guard_task
    if not input_guard_result.classification:
        urls_content_task.cancel()
        rag_content_task.cancel()

        logger.warning("Topical guardrail triggered")
        response = "sorry but i can't answer this :("
        await MessageRepository(session).create(
            MessageCreate(
                url_content="",
                rag_content="",
                request_content=body.prompt,
                response_content=response,
                thinking_content="Input Guardrails Triggered",
                conversation_id=conversation.id,
            )
        )
        return TextToTextResponse(result=response)

    urls_content = await urls_content_task
    rag_content = await rag_content_task

    if not body.prompt:
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
        urls_content
        if urls_content is not None
        else "urls content Couldn't be fetched",
        rag_content if rag_content is not None else "rag content Couldn't be fetched",
    ]
    full_prompt = "\n\n".join(prompt_parts)

    response, thinking = await client.ainvoke(
        system_prompt=None,
        user_query=body.prompt,
        other_prompt_content=full_prompt,
        model="gpt-oss:120b-cloud",
    )
    output_allowed = await output_guardrail.is_output_allowed(response)
    if output_allowed.classification:
        await MessageRepository(session).create(
            MessageCreate(
                url_content=urls_content,
                rag_content=rag_content,
                request_content=body.prompt,
                response_content=response,
                thinking_content=thinking,
                conversation_id=conversation.id,
            )
        )
        return TextToTextResponse(result=response)
    else:
        logger.warning("Output guardrail triggered — blocking response")
        new_response = "I'm unable to provide this response due to safety concerns."
        await MessageRepository(session).create(
            MessageCreate(
                url_content=urls_content,
                rag_content=rag_content,
                request_content=body.prompt,
                response_content=response,
                thinking_content="Output guardrail triggered",
                conversation_id=conversation.id,
            )
        )
        return TextToTextResponse(result=new_response)


@router.get("/stream/text-to-text/{conversation_id}")
async def stream_text_to_text(
    conversation: GetConversationDep,
    session: DBSessionDep,
    client: OllamaClientDep,
    input_guardrail: InputGuardrailDep,
    output_guardrail: OutputGuardrailDep,
    prompt: str = Query(...),
) -> StreamingResponse:
    # helper function to save messages while streaming
    async def stream_with_storage(
        stream: AsyncGenerator[str, None],
    ) -> AsyncGenerator[str, None]:
        stream_buffer = []
        thinking_buffer = []
        output_allowed = True
        final_response = ""
        try:
            async for chunk_type, chunk_text in stream:
                if chunk_type == "thinking":
                    thinking_buffer.append(chunk_text)
                elif chunk_type == "content":
                    stream_buffer.append(chunk_text)
                yield f"event: {chunk_type}\ndata: {chunk_text}\n\n"

            # Stream complete — run output guardrail before response closes
            final_response = "".join(stream_buffer)
            output_guard_result = await output_guardrail.is_output_allowed(
                final_response
            )
            output_allowed = output_guard_result.classification
            if not output_allowed:
                logger.warning("Output guardrail triggered — retracting response")
                yield "event: retracted\ndata: I'm unable to provide this response due to safety concerns.\n\n"
        finally:
            if not final_response:
                final_response = "".join(stream_buffer)

            final_thinking = "".join(thinking_buffer)

            await MessageRepository(session).create(
                MessageCreate.model_construct(
                    url_content=urls_content,
                    rag_content=rag_content,
                    request_content=prompt,
                    response_content=final_response,
                    thinking_content=final_thinking
                    if output_allowed
                    else "Output Guardrail Triggered",
                    conversation_id=conversation.id,
                )
            )

    # Manually fetch content using extracted service functions
    input_guard_task = asyncio.create_task(input_guardrail.is_input_allowed(prompt))
    urls_content_task = asyncio.create_task(fetch_urls_content(prompt))
    rag_content_task = asyncio.create_task(fetch_rag_content(prompt))

    input_guard_result = await input_guard_task
    if not input_guard_result.classification:
        urls_content_task.cancel()
        rag_content_task.cancel()

        logger.warning("Topical guardrail triggered")

        await MessageRepository(session).create(
            MessageCreate.model_construct(
                url_content="",
                rag_content="",
                request_content=prompt,
                response_content="sorry but i can't answer this :(",
                thinking_content="Input Guardrail Triggered",
                conversation_id=conversation.id,
            )
        )

        async def rejected_stream():
            yield "event: rejected\ndata: sorry but i can't answer this :(\n\n"

        return StreamingResponse(
            rejected_stream(),
            media_type="text/event-stream",
        )

    urls_content = await urls_content_task
    rag_content = await rag_content_task

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
        urls_content
        if urls_content is not None
        else "urls content Couldn't be fetched",
        rag_content if rag_content is not None else "rag content Couldn't be fetched",
    ]
    full_prompt = "\n\n".join(prompt_parts)

    response_stream = client.stream_chat(
        system_prompt=None,
        user_query=prompt,
        other_prompt_content=full_prompt,
        model="gpt-oss:120b-cloud",
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
    client: OllamaClientDep,
):
    logger.info("Connecting to client....")
    await ws_manager.connect(ws)
    try:
        while True:
            user_query = await ws_manager.receive(ws)
            # Manually fetch content using extracted service functions
            urls_content = await fetch_urls_content(user_query)
            rag_content = await fetch_rag_content(user_query)

            if not user_query:
                logger.warning("No prompt provided")
            if urls_content is None:
                logger.warning("No urls content provided")
            if rag_content is None:
                logger.warning("No rag content provided")

            prompt_parts = [
                urls_content
                if urls_content is not None
                else "urls content Couldn't be fetched",
                rag_content
                if rag_content is not None
                else "rag content Couldn't be fetched",
            ]
            other_prompt_content = "\n\n".join(prompt_parts)

            async for chunk_type, chunk_text in client.stream_chat(
                system_prompt=None,
                user_query=user_query,
                other_prompt_content=other_prompt_content,
                model="qwen3-vl:235b-instruct-cloud",
            ):
                await ws_manager.send(ws, {"type": chunk_type, "data": chunk_text})

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await ws_manager.send(ws, "an internal error occured!")
    finally:
        await ws_manager.disconnect(ws)
