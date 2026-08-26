"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="MoinSystems AI Chatbot",
    version="0.1.0",
    description="RAG-powered chatbot backend for MoinSystems AI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.get("/")
async def root():
    return {"service": "MoinSystems AI Chatbot", "status": "running"}