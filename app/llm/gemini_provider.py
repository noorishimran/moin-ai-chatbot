"""
Gemini LLM provider using the Google GenAI SDK.
"""

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.llm.base import LLMProvider


settings = get_settings()


class GeminiProvider(LLMProvider):
    """
    Gemini implementation of the common LLM provider interface.
    """

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Add it to the .env file."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    async def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a grounded assistant response using Gemini.
        """

        contents: list[types.Content] = []

        for message in messages:
            role = message.get("role")
            content = message.get("content", "").strip()

            if not content:
                continue

            if role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"

            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[
                        types.Part(
                            text=content
                        )
                    ],
                )
            )

        if not contents:
            raise ValueError(
                "No valid conversation messages were provided."
            )

        response = await self.client.aio.models.generate_content(
            model=settings.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True,
                ),
            ),
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text.strip()