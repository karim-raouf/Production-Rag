from fastapi import Depends
from app.core.config import AppSettings, get_settings
from .services.ollama_cloud_service import OllamaCloudChatClient
from .gaurdrails.input_gaurdrail import InputGuardrail


def get_ollama_client(
    settings: AppSettings = Depends(get_settings),
) -> OllamaCloudChatClient:
    return OllamaCloudChatClient(api_key=settings.ollama_api_key)


def get_input_guardrail(
    settings: AppSettings = Depends(get_settings),
) -> InputGuardrail:
    return InputGuardrail(api_key=settings.ollama_api_key)
