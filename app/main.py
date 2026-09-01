from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="RAG-based knowledge assistant orchestrated with n8n, FastAPI and pgvector.",
)

app.include_router(router)
