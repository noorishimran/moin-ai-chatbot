"""
Health check endpoint.
"""

from fastapi import APIRouter

from app.db.session import check_db_connection

router = APIRouter()


@router.get("/health")
async def health_check():
    db_ok = await check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }