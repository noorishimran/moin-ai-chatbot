"""
5.10 lead capture endpoint + 6.2-6.5 email notification wiring.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.models import (
    ChatMessage,
    ChatSession,
    EmailNotification,
    LeadSubmission,
)
from app.db.session import get_db
from app.email.service import send_lead_notification
from app.email.templates import build_lead_notification_email
from app.leads.state_machine import mark_complete
from app.schemas.lead import LeadCaptureRequest, LeadCaptureResponse


router = APIRouter()
settings = get_settings()


async def _last_user_question(
    db: AsyncSession,
    session_id,
) -> str | None:
    result = await db.execute(
        select(ChatMessage.content)
        .where(
            ChatMessage.session_id == session_id,
            ChatMessage.role == "user",
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(1)
    )

    row = result.first()

    return row[0] if row else None


@router.post(
    "/lead-capture",
    response_model=LeadCaptureResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def capture_lead(
    payload: LeadCaptureRequest,
    db: AsyncSession = Depends(get_db),
):
    # Find the active chat session.
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_token == payload.session_token
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Unknown session_token. Create a session first.",
        )

    # If a lead already exists for this session,
    # treat it as a successful/idempotent submission.
    existing_result = await db.execute(
        select(LeadSubmission).where(
            LeadSubmission.session_id == session.id
        )
    )

    existing_lead = existing_result.scalar_one_or_none()

    if existing_lead:
        return LeadCaptureResponse(
            lead_id=str(existing_lead.id)
        )

    # Create a new lead.
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

    # Flush so lead.id is available before creating
    # the email notification record.
    await db.flush()

    user_question = await _last_user_question(
        db,
        session.id,
    )

    subject, body = build_lead_notification_email(
        full_name=lead.full_name,
        email=lead.email,
        contact_number=lead.contact_number,
        service_interest=lead.service_interest,
        company_name=lead.company_name,
        project_summary=lead.project_summary,
        timeline=lead.timeline,
        budget_range=lead.budget_range,
        source_page=lead.source_page,
        user_question=user_question,
        conversation_summary=None,
    )

    send_result = await send_lead_notification(
        subject,
        body,
    )

    notification = EmailNotification(
        lead_id=lead.id,
        recipient=settings.lead_email_to,
        subject=subject,
        status="sent" if send_result.success else "failed",
        provider_message_id=send_result.provider_message_id,
        error_message=send_result.error,
        sent_at=(
            datetime.now(timezone.utc)
            if send_result.success
            else None
        ),
    )

    db.add(notification)

    await db.commit()

    return LeadCaptureResponse(
        lead_id=str(lead.id)
    )