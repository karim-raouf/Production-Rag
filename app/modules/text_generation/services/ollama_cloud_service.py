from ollama import AsyncClient
import ollama
from typing import AsyncGenerator
import asyncio
from ..gaurdrails.input_gaurdrail import is_topic_allowed
from loguru import logger


class OllamaCloudChatClient:
    def __init__(self, api_key: str, host: str = "https://ollama.com"):
        self.aclient = AsyncClient(
            host=host, headers={"Authorization": "Bearer " + api_key}
        )

    async def ainvoke(
        self,
        system_prompt: str | None,
        user_query: str,
        other_prompt_content: str,
        model: str,
        guardrails: bool = True,
    ) -> str:
        if not system_prompt:
            system_prompt = """ 
                You are a helpful assistant. use the context provided to answer the question,
                dont ever create info, if you dont know say i don't know,
            """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query + other_prompt_content},
        ]

        if guardrails:
            guard_task = asyncio.create_task(is_topic_allowed(user_query, self))
            chat_task = asyncio.create_task(
                self.aclient.chat(model, messages=messages, think="medium")
            )

            # Wait for guard result first
            guard_output = await guard_task
            if not guard_output.classification:
                chat_task.cancel()
                logger.warning("Topical guardrail triggered")
                return "sorry but i can't answer this :("

            # Guard passed — wait for chat if not already done
            chat_result = await chat_task
            return chat_result["message"]["content"]
        else:
            response = await self.aclient.chat(model, messages=messages, think="medium")
            return response["message"]["content"]

    async def stream_chat(
        self,
        system_prompt: str | None,
        user_query: str,
        other_prompt_content: str,
        model: str,
        stream_mode: str = "sse",
    ) -> AsyncGenerator[str, None]:
        if not system_prompt:
            system_prompt = """ 
                You are a helpful assistant. use the context provided to answer the question,
                dont ever create info, if you dont have context say i don't know as no context provided,
            """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query + other_prompt_content},
        ]
        guardrail_response = await is_topic_allowed(user_query, self)
        if not guardrail_response.classification:
            logger.warning("Topical guardrail triggered")
            yield (
                "data: sorry but i can't answer this :(\n\n"
                if stream_mode == "sse"
                else "sorry but i can't answer this :("
            )
            if stream_mode == "sse":
                yield "data: [DONE]\n\n"
            return
        try:
            async for token in await self.aclient.chat(
                model, messages=messages, stream=True, think="medium"
            ):
                thinking = token["message"].get("thinking")
                content = token["message"].get("content")

                if thinking:
                    yield (
                        f"data: [THINKING] {thinking}\n\n"
                        if stream_mode == "sse"
                        else f"[THINKING] {thinking}"
                    )
                    await asyncio.sleep(0.01)
                if content:
                    yield (f"data: {content}\n\n" if stream_mode == "sse" else content)
                    await asyncio.sleep(0.01)
            if stream_mode == "sse":
                yield "data: [DONE]\n\n"

        except ollama.ResponseError as e:
            print(f"Ollama Server Error: {e.error}")
            if e.status_code == 500:
                yield "Error: The Ollama server crashed. Check server logs or model availability."
            else:
                yield f"Error: Ollama returned status {e.status_code}"
