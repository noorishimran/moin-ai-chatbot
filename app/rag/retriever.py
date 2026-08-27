"""
RAG retriever service (Day 3).
"""

import re
from dataclasses import dataclass

from sqlalchemy import select, text

from app.core.config import get_settings
from app.db.models import KnowledgeChunk
from app.db.session import AsyncSessionLocal
from app.rag.embeddings import embed_text

settings = get_settings()

DEFAULT_TOP_K = 5
DEFAULT_MIN_SIMILARITY = 0.55


@dataclass
class RetrievedChunk:
    id: str
    title: str
    content: str
    category: str | None
    similarity: float


def normalize_query(query: str, recent_context: str | None = None) -> str:
    query = re.sub(r"\s+", " ", query).strip()
    if recent_context:
        recent_context = re.sub(r"\s+", " ", recent_context).strip()
        return f"{recent_context} {query}".strip()
    return query


async def retrieve(
    query: str,
    recent_context: str | None = None,
    top_k: int = DEFAULT_TOP_K,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
    category: str | None = None,
) -> list[RetrievedChunk]:
    prepared_query = normalize_query(query, recent_context)
    query_vector = embed_text(prepared_query, task_type="retrieval_query")

    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                KnowledgeChunk.id,
                KnowledgeChunk.title,
                KnowledgeChunk.content,
                KnowledgeChunk.category,
                (KnowledgeChunk.embedding.cosine_distance(query_vector)).label("distance"),
            )
            .order_by(text("distance ASC"))
            .limit(top_k)
        )
        if category:
            stmt = stmt.where(KnowledgeChunk.category == category)

        result = await session.execute(stmt)
        rows = result.all()

    results: list[RetrievedChunk] = []
    for row in rows:
        similarity = 1 - row.distance
        if similarity >= min_similarity:
            results.append(
                RetrievedChunk(
                    id=row.id,
                    title=row.title,
                    content=row.content,
                    category=row.category,
                    similarity=round(similarity, 4),
                )
            )

    seen_content: set[str] = set()
    deduped: list[RetrievedChunk] = []
    for r in results:
        fingerprint = r.content[:120].lower().strip()
        if fingerprint not in seen_content:
            seen_content.add(fingerprint)
            deduped.append(r)

    return deduped