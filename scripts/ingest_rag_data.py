"""
Day 2: RAG ingestion pipeline.

Reads the approved knowledge dataset, validates it, generates
embeddings, and upserts records into knowledge_document /
knowledge_chunk by stable ID (idempotent — safe to re-run).
"""

import asyncio
import re
import uuid

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.models import KnowledgeChunk, KnowledgeDocument
from app.db.session import AsyncSessionLocal
from app.rag.embeddings import embed_text

DATASET_PATH = "data/rag_dataset.xlsx"
DATASET_VERSION = "v2"
REQUIRED_COLUMNS = ["ID", "Title", "Category", "Tags", "Intents", "Content", "Data Status"]


def normalize_whitespace(text: str) -> str:
    """2.3 Normalization — collapse extra whitespace, keep meaning intact."""
    return re.sub(r"[ \t]+", " ", str(text)).strip()


def load_and_validate() -> pd.DataFrame:
    df = pd.read_excel(DATASET_PATH, sheet_name="RAG_Knowledge")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    # 2.1 — only ingest rows that actually have an ID (skip blank padding rows)
    df = df[df["ID"].notna()].copy()

    # Skip records that aren't approved yet (per SRS: source gaps stay excluded
    # until company-approved material is supplied)
    before = len(df)
    df = df[df["Data Status"] == "cleaned_validated"].copy()
    skipped = before - len(df)

    df["Content"] = df["Content"].apply(normalize_whitespace)
    df["Title"] = df["Title"].apply(normalize_whitespace)

    print(f"Loaded {before} total rows, {skipped} skipped (not cleaned_validated), {len(df)} ready to ingest.")
    return df


async def get_or_create_document(session) -> uuid.UUID:
    result = await session.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.source_name == "rag_dataset",
            KnowledgeDocument.version == DATASET_VERSION,
        )
    )
    doc = result.scalar_one_or_none()
    if doc:
        return doc.id

    doc = KnowledgeDocument(
        source_name="rag_dataset",
        version=DATASET_VERSION,
        source_uri=DATASET_PATH,
        status="active",
    )
    session.add(doc)
    await session.flush()
    return doc.id


async def main():
    df = load_and_validate()

    embedded_count = 0
    failed_ids = []

    async with AsyncSessionLocal() as session:
        document_id = await get_or_create_document(session)

        for _, row in df.iterrows():
            record_id = str(row["ID"])
            try:
                vector = embed_text(row["Content"])
            except Exception as e:
                failed_ids.append((record_id, str(e)))
                continue

            # 2.6 + 2.9 — upsert by stable ID, idempotent on re-run
            stmt = pg_insert(KnowledgeChunk).values(
                id=record_id,
                document_id=document_id,
                title=row["Title"],
                content=row["Content"],
                category=row.get("Category"),
                tags=row.get("Tags"),
                intents=row.get("Intents"),
                embedding=vector,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "title": stmt.excluded.title,
                    "content": stmt.excluded.content,
                    "category": stmt.excluded.category,
                    "tags": stmt.excluded.tags,
                    "intents": stmt.excluded.intents,
                    "embedding": stmt.excluded.embedding,
                    "document_id": stmt.excluded.document_id,
                },
            )
            await session.execute(stmt)
            embedded_count += 1

        await session.commit()

    # 2.10 — ingestion validation report
    print("\n--- Ingestion Validation Report ---")
    print(f"Dataset version: {DATASET_VERSION}")
    print(f"Records embedded/upserted: {embedded_count}")
    print(f"Records failed: {len(failed_ids)}")
    for rid, err in failed_ids:
        print(f"  - {rid}: {err}")
    print("------------------------------------")


if __name__ == "__main__":
    asyncio.run(main())