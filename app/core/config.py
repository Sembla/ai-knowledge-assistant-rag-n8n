from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Knowledge Assistant"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/knowledge_assistant"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-5.6-luna"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    retrieval_top_k: int = 4
    retrieval_min_score: float = 0.25
    chunk_size: int = 900
    chunk_overlap: int = 150

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
