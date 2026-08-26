"""
Quick Day-1 setup script: enables pgvector extension and creates all
tables from our models.
"""

import asyncio

from sqlalchemy import text

from app.db.models import Base
from app.db.session import engine


async def main():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    print("✅ pgvector extension enabled + all tables created.")


if __name__ == "__main__":
    asyncio.run(main())