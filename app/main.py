"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import chat, health, leads, sessions
from app.core.config import get_settings
from app.core.logging_setup import RequestLoggingMiddleware, setup_logging
from app.core.size_limit import BodySizeLimitMiddleware


settings = get_settings()
setup_logging()


app = FastAPI(
    title="MoinSystems AI Chatbot",
    version="0.1.0",
    description="RAG-powered chatbot backend for MoinSystems AI",
)

# 6.10 — reject oversized bodies before anything else runs
app.add_middleware(BodySizeLimitMiddleware)

# 6.11 — structured request logging
app.add_middleware(RequestLoggingMiddleware)

# 6.8 — CORS: only origins listed in .env (ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"],
)


app.include_router(
    chat.router,
    prefix="/api/v1",
    tags=["chat"],
)


app.include_router(
    sessions.router,
    prefix="/api/v1",
    tags=["sessions"],
)


app.include_router(
    leads.router,
    prefix="/api/v1",
    tags=["leads"],
)


@app.get("/")
async def root():
    return {
        "service": "MoinSystems AI Chatbot",
        "status": "running",
    }