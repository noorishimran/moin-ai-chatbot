"""
5.10 — lead capture endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatSession, LeadSubmission
from app.db.session import get_db
from app.leads.state_machine import mark_complete
from app.schemas.lead import LeadCaptureRequest, LeadCaptureResponse

router = APIRouter()


@router.post("/lead-capture", response_model=LeadCaptureResponse)
async def capture_lead(payload: LeadCaptureRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).where(ChatSession.session_token == payload.session_token))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Unknown session_token. Create a session first.")

    existing = await db.execute(select(LeadSubmission).where(LeadSubmission.session_id == session.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A lead has already been captured for this session.")

    lead = LeadSubmission(
        session_id=session.id,
        full_name=payload.full_name,
        email=payload.email,
        contact_number=payload.contact_number,
        company_name=payload.company_name,
        project_summary=payload.project_summary,
        service_interest=payload.service_interest,
        timeline=payload.timeline,
        budget_range=payload.budget_range,
        source_page=payload.source_page,
    )
    db.add(lead)

    await mark_complete(db, session)
    await db.commit()

    return LeadCaptureResponse(lead_id=str(lead.id))