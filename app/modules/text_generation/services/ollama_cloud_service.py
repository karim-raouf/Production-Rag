from ollama import AsyncClient

from typing import AsyncGenerator
import asyncio


class OllamaCloudChatClient:
    def __init__(self, api_key: str, host: str = "https://ollama.com"):
        self.aclient = AsyncClient(
            host=host, headers={"Authorization": "Bearer " + api_key}
        )

    async def stream_chat(self, prompt: str, model: str, stream_mode: str = "sse") -> AsyncGenerator[str, None]:
        system_prompt = """ 
            You are a helpful assistant. use the context provided to answer the question,
            dont ever create info, if you dont know say i don't know,
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        async for token in await self.aclient.chat(model, messages=messages, stream=True):
            if token['message']['content'] is not None:
                yield f"data: {token['message']['content'] or ''}\n\n" if stream_mode == "sse" else token['message']['content']
                await asyncio.sleep(0.01)
        if stream_mode == "sse":
            yield f"data: [DONE]\n\n"
