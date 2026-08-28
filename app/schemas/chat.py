"""
Request and response schemas for the chatbot API.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ConversationMessage(
    BaseModel
):
    """
    One validated conversation turn.
    """

    role: Literal[
        "user",
        "assistant",
    ]

    content: str = Field(
        min_length=1,
        max_length=5000,
    )


class ChatRequest(
    BaseModel
):
    """
    Incoming chat request.
    """

    message: str = Field(
        min_length=1,
        max_length=5000,
    )

    session_id: str | None = None

    history: list[
        ConversationMessage
    ] = Field(
        default_factory=list,
        max_length=20,
    )


class ChatResponse(
    BaseModel
):
    """
    Structured chatbot API response.
    """

    answer: str

    session_id: str | None = None

    intent: str

    next_state: str

    used_rag: bool