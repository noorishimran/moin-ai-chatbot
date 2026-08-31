"""
6.1 Email service adapter (SMTP).

Kept isolated so the retry/error-handling logic lives in exactly one
place, and swapping SMTP for a transactional email API later is a
change to this file only.
"""

import asyncio
import logging

import aiosmtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger("moin_ai.email")
settings = get_settings()

MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = [2, 5]  # wait before attempt 2, then attempt 3


class EmailSendResult:
    def __init__(self, success: bool, provider_message_id: str | None, error: str | None, attempts: int):
        self.success = success
        self.provider_message_id = provider_message_id
        self.error = error
        self.attempts = attempts


async def _send_once(subject: str, body: str, to_addr: str) -> str:
    """Raises on failure. Returns a provider message id on success."""
    message = EmailMessage()
    message["From"] = settings.smtp_username
    message["To"] = to_addr
    message["Subject"] = subject
    message.set_content(body)  # plain text only — see templates.py for why

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=True,
    )
    return message.get("Message-Id", "sent")


async def send_lead_notification(subject: str, body: str) -> EmailSendResult:
    """
    6.6 Retry behavior: up to MAX_ATTEMPTS on transient failures, with
    short backoff. Because this function is called once per lead (the
    caller persists a single EmailNotification row before calling),
    retries here update that same row's status rather than creating
    new notification rows — no duplicate emails from the retry loop
    itself (aiosmtplib.send either fully succeeds or raises; it does
    not partially send).
    """
    to_addr = settings.lead_email_to
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            provider_message_id = await _send_once(subject, body, to_addr)
            logger.info(f"email_sent attempt={attempt} to={to_addr}")
            return EmailSendResult(success=True, provider_message_id=provider_message_id, error=None, attempts=attempt)
        except Exception as e:
            last_error = str(e)
            logger.warning(f"email_send_failed attempt={attempt} error={last_error}")
            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS[attempt - 1])

    # 6.4 — sanitized error: don't leak SMTP internals/credentials into stored error text
    sanitized_error = "Email delivery failed after retries." if last_error else "Unknown email error."
    return EmailSendResult(success=False, provider_message_id=None, error=sanitized_error, attempts=MAX_ATTEMPTS)