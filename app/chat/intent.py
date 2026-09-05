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
    "start my project",
    "start development",
    "get started",
    "ready to start",
    "ready to hire",
    "build for me",
    "develop for me",
    "need a developer",
    "need an app",
    "need a chatbot",
    "work with you",
    "want to work with you",
    "want to build",
    "want to hire",
    "need your team",
    "contact me",
    "reach out to me",
    "contact me about",
    "reach out",
    "start working",
    "move forward",
    "proceed with the project",
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
    - high_intent
    - human_handoff
    - pricing
    - service_inquiry
    - general
    """

    if not message or not message.strip():
        return "general"

    text = message.lower().strip()

    # 1. Safety-critical requests always take top priority.
    if _contains_keyword(
        text,
        SENSITIVE_KEYWORDS,
    ):
        return "sensitive_data_request"

    # 2. Commercial / buying intent should trigger
    # the structured lead-capture form.
    if _contains_keyword(
        text,
        HIGH_INTENT_KEYWORDS,
    ):
        return "high_intent"

    # 3. Explicit human/legal/security handoff.
    if _contains_keyword(
        text,
        HUMAN_HANDOFF_KEYWORDS,
    ):
        return "human_handoff"

    # 4. Pricing alone should NOT automatically trigger a lead form.
    if _contains_keyword(
        text,
        PRICING_KEYWORDS,
    ):
        return "pricing"

    # 5. General service inquiry.
    if _contains_keyword(
        text,
        SERVICE_KEYWORDS,
    ):
        return "service_inquiry"

    return "general"