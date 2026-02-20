from fastapi import Depends
from app.core.config import AppSettings, get_settings
from .services.ollama_cloud_service import OllamaCloudChatClient
from .guardrails.input_guardrail import InputGuardrail
from .guardrails.output_guardrail import OutputGuardrail
from typing import Annotated
from loguru import logger
from ...core import api_limiters
from ...core.api_limiters import get_user_id
from fastapi import Response, Request
from fastapi_limiter.depends import RateLimiter



def get_ollama_client(
    settings: AppSettings = Depends(get_settings),
) -> OllamaCloudChatClient:
    return OllamaCloudChatClient(api_key=settings.ollama_api_key)


def get_input_guardrail(
    settings: AppSettings = Depends(get_settings),
) -> InputGuardrail:
    return InputGuardrail(api_key=settings.ollama_api_key)


def get_output_guardrail(
    settings: AppSettings = Depends(get_settings),
) -> OutputGuardrail:
    return OutputGuardrail(api_key=settings.ollama_api_key)


OllamaClientDep = Annotated[OllamaCloudChatClient, Depends(get_ollama_client)]

InputGuardrailDep = Annotated[InputGuardrail, Depends(get_input_guardrail)]

OutputGuardrailDep = Annotated[OutputGuardrail, Depends(get_output_guardrail)]



# ---------------------- API LIMITS ---------------------------------------

async def limit_text_gen(request: Request, response: Response):
    if api_limiters.text_limiter:
        await RateLimiter(limiter=api_limiters.text_limiter, identifier=get_user_id)(
            request, response
        )
    else:
        logger.warning("Text limiter not initialized")