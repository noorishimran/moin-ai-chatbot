"""
Base interface for LLM providers.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Common interface for all supported LLM providers.
    """

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate an assistant response.
        """
        raise NotImplementedError