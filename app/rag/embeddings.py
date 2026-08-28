"""
Gemini embedding wrapper using the Google GenAI SDK.
"""

from google import genai
from google.genai import types

from app.core.config import get_settings


settings = get_settings()

client = genai.Client(
    api_key=settings.gemini_api_key
)


def embed_text(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[float]:
    """
    Generate a 768-dimensional embedding vector.
    """

    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing."
        )

    response = client.models.embed_content(
        model=settings.embedding_model,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=768,
        ),
    )

    if not response.embeddings:
        raise RuntimeError(
            "Gemini returned no embedding."
        )

    values = response.embeddings[0].values

    if not values:
        raise RuntimeError(
            "Gemini returned an empty embedding."
        )

    return list(values)