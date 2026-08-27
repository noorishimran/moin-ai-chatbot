"""
Gemini embedding wrapper.
"""

import google.generativeai as genai

from app.core.config import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)


def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    """
    Returns a 768-dim embedding vector using Gemini's gemini-embedding-001 model.
    """
    result = genai.embed_content(
        model=f"models/{settings.embedding_model}",
        content=text,
        task_type=task_type,
        output_dimensionality=768,
    )
    return result["embedding"]