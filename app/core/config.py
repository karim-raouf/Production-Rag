from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated
from pydantic import Field


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    upload_chunk_size: Annotated[int, Field(alias="UPLOAD_CHUNK_SIZE")]
    rag_chunk_size: Annotated[int, Field(alias="RAG_CHUNK_SIZE")]
    embed_size: Annotated[int, Field(alias="EMBEDDING_SIZE")]

    qdrant_host: Annotated[str, Field(alias="QDRANT_HOST")]
    qdrant_port: Annotated[int, Field(alias="QDRANT_PORT")]

    vllm_api_key: Annotated[str, Field(alias="VLLM_API_KEY")]
    ollama_api_key: Annotated[str, Field(alias="OLLAMA_API_KEY")]

    postgres_url: Annotated[str, Field(alias="POSTGRES_URL")]

    # JWT Settings
    jwt_secret_key: Annotated[str, Field(alias="JWT_SECRET_KEY")]
    jwt_algorithm: Annotated[str, Field(alias="JWT_ALGORITHM")]
    jwt_expires_in_minutes: Annotated[int, Field(alias="JWT_EXPIRES_IN_MINUTES")]


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
