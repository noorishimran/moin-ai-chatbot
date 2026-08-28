"""
Remove outdated RAG records that conflict with the current SRS.

The current SRS explicitly excludes CRM from the chatbot's
lead-capture workflow.
"""

import asyncio

from sqlalchemy import delete, select

from app.db.models import KnowledgeChunk
from app.db.session import AsyncSessionLocal


OUTDATED_RECORD_IDS = [
    "phase2_pricing_001",
    "phase2_lead_capture_001",
    "phase2_email_001",
]


async def main() -> None:
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(KnowledgeChunk.id).where(
                KnowledgeChunk.id.in_(
                    OUTDATED_RECORD_IDS
                )
            )
        )

        existing_ids = list(
            result.scalars().all()
        )

        if not existing_ids:
            print(
                "No outdated CRM workflow "
                "records found in the database."
            )
            return

        print(
            "Outdated records found:"
        )

        for record_id in existing_ids:
            print(
                f"  - {record_id}"
            )

        await session.execute(
            delete(KnowledgeChunk).where(
                KnowledgeChunk.id.in_(
                    existing_ids
                )
            )
        )

        await session.commit()

        print(
            f"\nDeleted {len(existing_ids)} "
            f"outdated RAG record(s)."
        )


if __name__ == "__main__":
    asyncio.run(
        main()
    )