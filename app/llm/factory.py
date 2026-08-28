"""
Factory for selecting the configured LLM provider.
"""

from app.core.config import get_settings
from app.llm.base import LLMProvider
from app.llm.gemini_provider import GeminiProvider


settings = get_settings()


def get_llm_provider() -> LLMProvider:
    """
    Return the configured LLM provider.
    """

    provider = settings.llm_provider.lower().strip()

    if provider == "gemini":
        return GeminiProvider()

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )