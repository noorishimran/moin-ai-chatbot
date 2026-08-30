"""
5.1 / 5.10 — explicit session bootstrap endpoint.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatSession
from app.db.session import get_db
from app.schemas.lead import SessionCreateRequest, SessionCreateResponse

router = APIRouter()


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(payload: SessionCreateRequest, db: AsyncSession = Depends(get_db)):
    session = ChatSession(
        session_token=str(uuid.uuid4()),
        source_page=payload.source_page,
    )
    db.add(session)
    await db.commit()
    return SessionCreateResponse(session_token=session.session_token)