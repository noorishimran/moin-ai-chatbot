"""
5.4 Lead-capture state machine.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatSession

VALID_STATES = {"not_started", "collecting", "complete"}


async def mark_collecting(db: AsyncSession, session: ChatSession) -> None:
    if session.lead_capture_state == "not_started":
        session.lead_capture_state = "collecting"
        await db.flush()


async def mark_complete(db: AsyncSession, session: ChatSession) -> None:
    session.lead_capture_state = "complete"
    await db.flush()


def missing_required_fields(full_name: str | None, email: str | None, contact_number: str | None) -> list[str]:
    missing = []
    if not full_name:
        missing.append("full_name")
    if not email:
        missing.append("email")
    if not contact_number:
        missing.append("contact_number")
    return missing