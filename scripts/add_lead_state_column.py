"""
Day 5: adds lead_capture_state to chat_session WITHOUT touching
existing tables/data — especially knowledge_chunk, whose embeddings
took real API calls to generate and must not be lost.
"""

import asyncio

from sqlalchemy import text

from app.db.session import engine


async def main():
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "ALTER TABLE chat_session "
                "ADD COLUMN IF NOT EXISTS lead_capture_state VARCHAR(32) "
                "NOT NULL DEFAULT 'not_started';"
            )
        )
    print("✅ chat_session.lead_capture_state column ready.")


if __name__ == "__main__":
    asyncio.run(main())