"""
Public chatbot API routes.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.chat.orchestrator import generate_chat_response
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/chat/messages",
    response_model=ChatResponse,
)
async def send_chat_message(
    payload: ChatRequest,
) -> ChatResponse:
    """
    Send a visitor message and receive a grounded AI response.
    """

    try:
        history = [
            item.model_dump()
            for item in payload.history
        ]

        result = await generate_chat_response(
            message=payload.message,
            history=history,
            session_id=payload.session_id,
        )

        return ChatResponse(**result)

    except Exception as exc:
        logger.exception(
            "Chat processing failed",
            extra={
                "session_id": payload.session_id,
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to process the chat message.",
        ) from exc