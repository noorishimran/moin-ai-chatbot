# app/chat/orchestrator.py

"""
Chat orchestration service.

Flow:
user message
-> intent detection
-> deterministic safety / handoff rules
-> recent conversation context
-> RAG retrieval
-> context building
-> system prompt
-> configured LLM provider
-> grounded response
"""

import logging

from app.chat.intent import detect_intent
from app.llm.factory import get_llm_provider
from app.rag.context_builder import build_context
from app.rag.prompts import (
    UNKNOWN_FALLBACK,
    build_system_prompt,
)
from app.rag.retriever import retrieve


logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 6


LLM_FAILURE_MESSAGE = (
    "I'm having trouble generating a response right now. "
    "Please try again in a moment, or I can connect you "
    "with the MoinSystems AI team."
)


SENSITIVE_DATA_MESSAGE = (
    "I can't collect passwords, API keys, payment-card details, "
    "or other private credentials here. For security-sensitive "
    "assistance, I can direct you to the MoinSystems AI team."
)


HUMAN_HANDOFF_MESSAGE = (
    "Of course. This is best handled by the MoinSystems AI team. "
    "I can direct you to the team for further assistance."
)


HIGH_INTENT_MESSAGE = (
    "Absolutely. Please use the short form below to share your contact "
    "details and project requirements. The MoinSystems AI team can then "
    "follow up with you directly."
)


async def generate_chat_response(
    message: str,
    history: list[dict[str, str]] | None = None,
    session_id: str | None = None,
) -> dict:
    """
    Generate one grounded chatbot response.
    """

    # -------------------------------------------------
    # 1. Detect user intent
    # -------------------------------------------------
    intent = detect_intent(message)

    # -------------------------------------------------
    # 2. Sensitive-data safety short-circuit
    # -------------------------------------------------
    if intent == "sensitive_data_request":
        return {
            "answer": SENSITIVE_DATA_MESSAGE,
            "session_id": session_id,
            "intent": intent,
            "next_state": "human_handoff",
            "used_rag": False,
        }

    # -------------------------------------------------
    # 3. Explicit human / legal / security handoff
    # -------------------------------------------------
    if intent == "human_handoff":
        return {
            "answer": HUMAN_HANDOFF_MESSAGE,
            "session_id": session_id,
            "intent": intent,
            "next_state": "human_handoff",
            "used_rag": False,
        }

    # -------------------------------------------------
    # 4. High-intent lead capture
    # Do NOT ask for lead details inside the LLM chat.
    # The frontend form is the single structured capture path.
    # -------------------------------------------------
    if intent == "high_intent":
        return {
            "answer": HIGH_INTENT_MESSAGE,
            "session_id": session_id,
            "intent": intent,
            "next_state": "lead_capture_pending",
            "used_rag": False,
        }

    # -------------------------------------------------
    # 5. Limit and validate conversation history
    # -------------------------------------------------
    raw_history = (history or [])[-MAX_HISTORY_MESSAGES:]

    recent_history: list[dict[str, str]] = []

    for item in raw_history:
        role = item.get("role")
        content = item.get("content")

        if (
            role in {"user", "assistant"}
            and isinstance(content, str)
            and content.strip()
        ):
            recent_history.append(
                {
                    "role": role,
                    "content": content.strip(),
                }
            )

    # -------------------------------------------------
    # 6. Build small retrieval conversation context
    # -------------------------------------------------
    recent_context = None

    recent_user_messages = [
        item["content"]
        for item in recent_history
        if item["role"] == "user"
    ]

    if recent_user_messages:
        recent_context = " ".join(
            recent_user_messages[-2:]
        )

    # -------------------------------------------------
    # 7. Retrieve approved company knowledge
    # -------------------------------------------------
    chunks = await retrieve(
        query=message,
        recent_context=recent_context,
    )

    # -------------------------------------------------
    # 8. Unknown / insufficient-context handling
    # -------------------------------------------------
    if not chunks:
        return {
            "answer": UNKNOWN_FALLBACK,
            "session_id": session_id,
            "intent": "unknown",
            "next_state": "human_handoff",
            "used_rag": False,
        }

    # -------------------------------------------------
    # 9. Build deterministic RAG context
    # -------------------------------------------------
    knowledge_context = build_context(chunks)

    if not knowledge_context.strip():
        return {
            "answer": UNKNOWN_FALLBACK,
            "session_id": session_id,
            "intent": "unknown",
            "next_state": "human_handoff",
            "used_rag": False,
        }

    # -------------------------------------------------
    # 10. Normal conversation state
    # -------------------------------------------------
    lead_state = "inactive"
    next_state = "general_query"

    # -------------------------------------------------
    # 11. Build layered system prompt
    # -------------------------------------------------
    system_prompt = build_system_prompt(
        knowledge_context=knowledge_context,
        intent=intent,
        lead_state=lead_state,
    )

    # -------------------------------------------------
    # 12. Prepare recent conversation for the LLM
    # -------------------------------------------------
    llm_messages: list[dict[str, str]] = list(recent_history)

    llm_messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    # -------------------------------------------------
    # 13. Generate grounded response
    # -------------------------------------------------
    try:
        provider = get_llm_provider()

        answer = await provider.generate(
            system_prompt=system_prompt,
            messages=llm_messages,
        )

    except Exception:
        logger.exception(
            "LLM generation failed",
            extra={
                "session_id": session_id,
                "intent": intent,
            },
        )

        return {
            "answer": LLM_FAILURE_MESSAGE,
            "session_id": session_id,
            "intent": intent,
            "next_state": "human_handoff",
            "used_rag": True,
        }

    # -------------------------------------------------
    # 14. Protect against empty response
    # -------------------------------------------------
    if not answer or not answer.strip():
        logger.warning(
            "LLM returned an empty answer",
            extra={
                "session_id": session_id,
                "intent": intent,
            },
        )

        return {
            "answer": LLM_FAILURE_MESSAGE,
            "session_id": session_id,
            "intent": intent,
            "next_state": "human_handoff",
            "used_rag": True,
        }

    # -------------------------------------------------
    # 15. Return structured API result
    # -------------------------------------------------
    return {
        "answer": answer.strip(),
        "session_id": session_id,
        "intent": intent,
        "next_state": next_state,
        "used_rag": True,
    }