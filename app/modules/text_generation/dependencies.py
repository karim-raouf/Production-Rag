from fastapi import Depends
from app.core.config import AppSettings, get_settings
from .services.ollama_cloud_service import OllamaCloudChatClient
from .gaurdrails.input_gaurdrail import InputGuardrail
from .gaurdrails.output_gaurdrail import OutputGuardrail
from typing import Annotated



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