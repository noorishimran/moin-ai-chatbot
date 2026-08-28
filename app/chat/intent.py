"""
Lightweight intent routing for Day 4.

The complete persistent lead-capture state machine is implemented
during Day 5. This module performs the routing needed by the
Day 4 chat orchestration layer.
"""

import re


SENSITIVE_KEYWORDS = [
    "password",
    "api key",
    "apikey",
    "secret key",
    "private key",
    "credential",
    "credentials",
    "credit card",
    "card number",
    "cvv",
    "otp",
]


HUMAN_HANDOFF_KEYWORDS = [
    "speak to a human",
    "talk to a human",
    "speak to a person",
    "talk to a person",
    "speak to someone",
    "talk to someone",
    "human agent",
    "representative",
    "contact the team",
    "talk to your team",
    "speak to your team",
    "legal issue",
    "legal question",
    "contract question",
    "contract issue",
    "security issue",
]


HIGH_INTENT_KEYWORDS = [
    "hire",
    "hire you",
    "start a project",
    "build for me",
    "develop for me",
    "need a developer",
    "need an app",
    "need a chatbot",
    "work with you",
    "want to build",
    "want to hire",
    "need your team",
]


PRICING_KEYWORDS = [
    "price",
    "pricing",
    "cost",
    "quote",
    "quotation",
    "how much",
    "budget",
    "estimate",
]


SERVICE_KEYWORDS = [
    "service",
    "services",
    "develop",
    "development",
    "project",
    "chatbot",
    "website",
    "web app",
    "mobile app",
    "saas",
    "mvp",
    "automation",
    "ai solution",
    "ai development",
    "integration",
]


def _contains_keyword(
    text: str,
    keywords: list[str],
) -> bool:
    """
    Check whether any configured keyword appears as a complete
    phrase/word in the normalized user message.
    """

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"

        if re.search(pattern, text):
            return True

    return False


def detect_intent(
    message: str | None,
) -> str:
    """
    Classify the visitor message into a basic application intent.

    Possible values:
    - sensitive_data_request
    - human_handoff
    - high_intent
    - pricing
    - service_inquiry
    - general
    """

    if not message or not message.strip():
        return "general"

    text = message.lower().strip()

    # Safety-critical requests must be handled before
    # retrieval or LLM generation.
    if _contains_keyword(
        text,
        SENSITIVE_KEYWORDS,
    ):
        return "sensitive_data_request"

    # Explicit human, legal, contract, or security requests
    # should move to human handoff.
    if _contains_keyword(
        text,
        HUMAN_HANDOFF_KEYWORDS,
    ):
        return "human_handoff"

    # High buying intent takes priority over simple pricing.
    if _contains_keyword(
        text,
        HIGH_INTENT_KEYWORDS,
    ):
        return "high_intent"

    if _contains_keyword(
        text,
        PRICING_KEYWORDS,
    ):
        return "pricing"

    if _contains_keyword(
        text,
        SERVICE_KEYWORDS,
    ):
        return "service_inquiry"

    return "general"