"""
Lead capture endpoint + email notification wiring.
"""

import asyncio
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

EMAIL_TIMEOUT_SECONDS = 25


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


async def _latest_notification(
    db: AsyncSession,
    lead_id,
) -> EmailNotification | None:
    result = await db.execute(
        select(EmailNotification)
        .where(
            EmailNotification.lead_id == lead_id
        )
        .order_by(
            EmailNotification.created_at.desc()
        )
        .limit(1)
    )

    return result.scalar_one_or_none()


@router.post(
    "/lead-capture",
    response_model=LeadCaptureResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def capture_lead(
    payload: LeadCaptureRequest,
    db: AsyncSession = Depends(get_db),
):
    # -------------------------------------------------
    # 1. Validate session
    # -------------------------------------------------
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_token
            == payload.session_token
        )
    )

    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=404,
            detail=(
                "Unknown session_token. "
                "Create a session first."
            ),
        )

    # -------------------------------------------------
    # 2. Idempotent duplicate handling
    # -------------------------------------------------
    existing_result = await db.execute(
        select(LeadSubmission).where(
            LeadSubmission.session_id
            == session.id
        )
    )

    existing_lead = (
        existing_result.scalar_one_or_none()
    )

    if existing_lead:
        notification = await _latest_notification(
            db,
            existing_lead.id,
        )

        if (
            notification
            and notification.status == "sent"
        ):
            return LeadCaptureResponse(
                lead_id=str(existing_lead.id),
                status="saved",
                email_status="sent",
                message=(
                    "Your details were already submitted "
                    "successfully."
                ),
            )

        return LeadCaptureResponse(
            lead_id=str(existing_lead.id),
            status="saved_email_failed",
            email_status="failed",
            message=(
                "Your details have already been saved, "
                "but the email notification was not sent."
            ),
        )

    # -------------------------------------------------
    # 3. Create lead
    # -------------------------------------------------
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

    await mark_complete(
        db,
        session,
    )

    # Generate lead.id.
    await db.flush()

    user_question = await _last_user_question(
        db,
        session.id,
    )

    # -------------------------------------------------
    # 4. Build notification email
    # -------------------------------------------------
    subject, body = (
        build_lead_notification_email(
            full_name=lead.full_name,
            email=lead.email,
            contact_number=(
                lead.contact_number
            ),
            service_interest=(
                lead.service_interest
            ),
            company_name=lead.company_name,
            project_summary=(
                lead.project_summary
            ),
            timeline=lead.timeline,
            budget_range=lead.budget_range,
            source_page=lead.source_page,
            user_question=user_question,
            conversation_summary=None,
        )
    )

    # -------------------------------------------------
    # 5. Attempt email with bounded timeout
    # -------------------------------------------------
    try:
        send_result = await asyncio.wait_for(
            send_lead_notification(
                subject,
                body,
            ),
            timeout=EMAIL_TIMEOUT_SECONDS,
        )

        email_success = send_result.success

        provider_message_id = (
            send_result.provider_message_id
        )

        email_error = send_result.error

    except asyncio.TimeoutError:
        email_success = False
        provider_message_id = None
        email_error = (
            "Email delivery timed out."
        )

    except Exception:
        email_success = False
        provider_message_id = None
        email_error = (
            "Email delivery failed."
        )

    # -------------------------------------------------
    # 6. Save notification result
    # -------------------------------------------------
    notification = EmailNotification(
        lead_id=lead.id,
        recipient=settings.lead_email_to,
        subject=subject,
        status=(
            "sent"
            if email_success
            else "failed"
        ),
        provider_message_id=(
            provider_message_id
        ),
        error_message=email_error,
        sent_at=(
            datetime.now(timezone.utc)
            if email_success
            else None
        ),
    )

    db.add(notification)

    # -------------------------------------------------
    # 7. Persist lead + notification result
    # -------------------------------------------------
    await db.commit()

    # -------------------------------------------------
    # 8. Return truthful result
    # -------------------------------------------------
    if email_success:
        return LeadCaptureResponse(
            lead_id=str(lead.id),
            status="saved",
            email_status="sent",
            message=(
                "Thanks! Your details were submitted "
                "successfully and the MoinSystems AI "
                "team has been notified."
            ),
        )

    return LeadCaptureResponse(
        lead_id=str(lead.id),
        status="saved_email_failed",
        email_status="failed",
        message=(
            "Your details were saved successfully, "
            "but the team notification email could "
            "not be sent right now."
        ),
    )