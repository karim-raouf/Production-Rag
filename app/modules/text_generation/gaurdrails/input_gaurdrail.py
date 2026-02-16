from __future__ import annotations
from typing import TYPE_CHECKING
from .schema import TopicalGuardResponse

if TYPE_CHECKING:
    from ..services.ollama_cloud_service import OllamaCloudChatClient


async def is_topic_allowed(
    user_query: str, client: OllamaCloudChatClient
) -> TopicalGuardResponse:
    guardrail_system_prompt = """
    Your role is to assess user queries as valid or invalid
    Allowed topics include:
    1. API Development
    2. FastAPI
    3. Building Generative AI systems
    If a topic is allowed, say 'True' otherwise say 'False'
    """
    response = await client.ainvoke(
        system_prompt=guardrail_system_prompt,
        user_query=user_query,
        other_prompt_content="",
        model="ministral-3:14b-cloud",
        guardrails=False,
    )
    return TopicalGuardResponse(classification=response)
