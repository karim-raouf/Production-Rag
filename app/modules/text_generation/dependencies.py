from fastapi import Depends
from app.core.config import AppSettings, get_settings
from .services.ollama_cloud_service import OllamaCloudChatClient


def get_ollama_client(
    settings: AppSettings = Depends(get_settings),
) -> OllamaCloudChatClient:
    return OllamaCloudChatClient(api_key=settings.ollama_api_key)
