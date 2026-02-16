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
            chat_task = asyncio.create_task(self.aclient.chat(model, messages=messages))

            while True:
                done, _ = await asyncio.wait(
                    [guard_task, chat_task], return_when=asyncio.FIRST_COMPLETED
                )
                if guard_task in done:
                    guard_output = guard_task.result()
                    if not (allowed := guard_output.classification):
                        chat_task.cancel()
                        logger.warning("Topical guardrail triggered")
                        return "sorry but i can't answer this :("
                    elif chat_task in done:
                        return chat_task.result()["message"]["content"]
                else:
                    await asyncio.sleep(0.1)

        response = await self.aclient.chat(model, messages=messages)
        return response["message"]["content"]

    async def stream_chat(
        self, prompt: str, model: str, stream_mode: str = "sse"
    ) -> AsyncGenerator[str, None]:
        system_prompt = """ 
            You are a helpful assistant. use the context provided to answer the question,
            dont ever create info, if you dont have context say i don't know as no context provided,
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        try:
            async for token in await self.aclient.chat(
                model, messages=messages, stream=True
            ):
                if token["message"]["content"] is not None:
                    yield (
                        f"data: {token['message']['content'] or ''}\n\n"
                        if stream_mode == "sse"
                        else token["message"]["content"]
                    )
                    await asyncio.sleep(0.01)
            if stream_mode == "sse":
                yield f"data: [DONE]\n\n"

        except ollama.ResponseError as e:
            print(f"Ollama Server Error: {e.error}")
            if e.status_code == 500:
                yield "Error: The Ollama server crashed. Check server logs or model availability."
            else:
                yield f"Error: Ollama returned status {e.status_code}"
