"""
Day 2: RAG ingestion pipeline.

Reads the approved knowledge dataset, validates it, generates
embeddings, and upserts records into knowledge_document /
knowledge_chunk by stable ID.

Idempotent: safe to re-run.
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

REQUIRED_COLUMNS = [
    "ID",
    "Title",
    "Category",
    "Tags",
    "Intents",
    "Content",
    "Data Status",
]

# These records conflict with the current SRS because they describe
# the chatbot's own lead workflow as CRM-based.
# The current SRS explicitly excludes CRM from this project.
EXCLUDED_OUTDATED_RECORD_IDS = {
    "phase2_pricing_001",
    "phase2_lead_capture_001",
    "phase2_email_001",
}


def normalize_whitespace(text: str) -> str:
    """
    Collapse extra whitespace while preserving meaning.
    """

    return re.sub(
        r"[ \t]+",
        " ",
        str(text),
    ).strip()


def clean_optional_value(value):
    """
    Convert NaN/blank optional spreadsheet values to None.
    """

    if pd.isna(value):
        return None

    text = normalize_whitespace(value)

    return text if text else None


def load_and_validate() -> pd.DataFrame:
    """
    Load and validate the approved public RAG knowledge sheet.
    """

    df = pd.read_excel(
        DATASET_PATH,
        sheet_name="RAG_Knowledge",
    )

    missing_cols = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_cols:
        raise ValueError(
            f"Dataset missing required columns: {missing_cols}"
        )

    # Ignore blank spreadsheet padding rows.
    df = df[
        df["ID"].notna()
    ].copy()

    total_rows = len(df)

    # Only ingest approved/validated records.
    df = df[
        df["Data Status"] == "cleaned_validated"
    ].copy()

    status_skipped = (
        total_rows - len(df)
    )

    # Current SRS supersedes older CRM-based chatbot workflow records.
    outdated_mask = df["ID"].astype(str).isin(
        EXCLUDED_OUTDATED_RECORD_IDS
    )

    outdated_skipped = int(
        outdated_mask.sum()
    )

    df = df[
        ~outdated_mask
    ].copy()

    # Normalize stable IDs.
    df["ID"] = (
        df["ID"]
        .astype(str)
        .str.strip()
    )

    # Reject duplicate stable IDs.
    duplicate_ids = (
        df[df["ID"].duplicated(keep=False)]["ID"]
        .tolist()
    )

    if duplicate_ids:
        raise ValueError(
            "Duplicate dataset IDs found: "
            f"{sorted(set(duplicate_ids))}"
        )

    # Required searchable fields.
    df["Title"] = df["Title"].apply(
        normalize_whitespace
    )

    df["Content"] = df["Content"].apply(
        normalize_whitespace
    )

    # Remove rows with no usable searchable text.
    empty_content_mask = (
        df["Content"].str.len() == 0
    )

    empty_content_skipped = int(
        empty_content_mask.sum()
    )

    df = df[
        ~empty_content_mask
    ].copy()

    print(
        f"Loaded {total_rows} total rows."
    )

    print(
        f"Skipped {status_skipped} rows "
        f"because Data Status was not cleaned_validated."
    )

    print(
        f"Skipped {outdated_skipped} outdated CRM-workflow records "
        f"because they conflict with the current SRS."
    )

    print(
        f"Skipped {empty_content_skipped} rows "
        f"with empty content."
    )

    print(
        f"{len(df)} records ready to ingest."
    )

    return df


async def get_or_create_document(
    session,
) -> uuid.UUID:
    """
    Return the knowledge-document row for this dataset version,
    creating it if necessary.
    """

    result = await session.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.source_name
            == "rag_dataset",
            KnowledgeDocument.version
            == DATASET_VERSION,
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


async def main() -> None:
    """
    Run full dataset ingestion.
    """

    df = load_and_validate()

    embedded_count = 0
    failed_ids: list[
        tuple[str, str]
    ] = []

    async with AsyncSessionLocal() as session:

        document_id = (
            await get_or_create_document(
                session
            )
        )

        for _, row in df.iterrows():

            record_id = str(
                row["ID"]
            ).strip()

            try:
                vector = embed_text(
                    row["Content"],
                    task_type="RETRIEVAL_DOCUMENT",
                )

            except Exception as exc:
                failed_ids.append(
                    (
                        record_id,
                        str(exc),
                    )
                )

                continue

            stmt = pg_insert(
                KnowledgeChunk
            ).values(
                id=record_id,
                document_id=document_id,
                title=row["Title"],
                content=row["Content"],
                category=clean_optional_value(
                    row.get("Category")
                ),
                tags=clean_optional_value(
                    row.get("Tags")
                ),
                intents=clean_optional_value(
                    row.get("Intents")
                ),
                embedding=vector,
            )

            stmt = (
                stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        "title":
                            stmt.excluded.title,
                        "content":
                            stmt.excluded.content,
                        "category":
                            stmt.excluded.category,
                        "tags":
                            stmt.excluded.tags,
                        "intents":
                            stmt.excluded.intents,
                        "embedding":
                            stmt.excluded.embedding,
                        "document_id":
                            stmt.excluded.document_id,
                    },
                )
            )

            await session.execute(
                stmt
            )

            embedded_count += 1

        await session.commit()

    print(
        "\n--- Ingestion Validation Report ---"
    )

    print(
        f"Dataset version: "
        f"{DATASET_VERSION}"
    )

    print(
        f"Records embedded/upserted: "
        f"{embedded_count}"
    )

    print(
        f"Records failed: "
        f"{len(failed_ids)}"
    )

    if failed_ids:
        for record_id, error in failed_ids:
            print(
                f"  - {record_id}: {error}"
            )

    print(
        "------------------------------------"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )