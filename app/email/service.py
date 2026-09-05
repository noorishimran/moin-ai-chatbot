"""
6.1 Email service adapter (SMTP).

Kept isolated so the retry/error-handling logic lives in exactly one
place, and swapping SMTP for a transactional email API later is a
change to this file only.
"""

import asyncio
import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import get_settings


logger = logging.getLogger("moin_ai.email")
settings = get_settings()


# Maximum number of SMTP attempts for one notification.
MAX_ATTEMPTS = 3

# Wait before attempt 2 and attempt 3.
RETRY_BACKOFF_SECONDS = [2, 5]

# Prevent a single SMTP connection attempt from hanging
# for too long.
SMTP_TIMEOUT_SECONDS = 8


class EmailSendResult:
    def __init__(
        self,
        success: bool,
        provider_message_id: str | None,
        error: str | None,
        attempts: int,
    ):
        self.success = success
        self.provider_message_id = provider_message_id
        self.error = error
        self.attempts = attempts


async def _send_once(
    subject: str,
    body: str,
    to_addr: str,
) -> str:
    """
    Send one SMTP email attempt.

    Raises an exception on failure.
    Returns a provider/message identifier on success.
    """

    message = EmailMessage()

    message["From"] = settings.smtp_username
    message["To"] = to_addr
    message["Subject"] = subject

    # Plain-text notification email.
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        start_tls=True,
        timeout=SMTP_TIMEOUT_SECONDS,
    )

    return message.get("Message-Id", "sent")


async def send_lead_notification(
    subject: str,
    body: str,
) -> EmailSendResult:
    """
    Send the internal lead notification.

    Retries transient SMTP failures up to MAX_ATTEMPTS.
    Returns a structured result instead of exposing SMTP
    exceptions to the API layer.
    """

    to_addr = settings.lead_email_to
    last_error: str | None = None

    for attempt in range(
        1,
        MAX_ATTEMPTS + 1,
    ):
        try:
            provider_message_id = await _send_once(
                subject,
                body,
                to_addr,
            )

            logger.info(
                "email_sent attempt=%s to=%s",
                attempt,
                to_addr,
            )

            return EmailSendResult(
                success=True,
                provider_message_id=provider_message_id,
                error=None,
                attempts=attempt,
            )

        except Exception as exc:
            last_error = str(exc)

            logger.warning(
                "email_send_failed attempt=%s error=%s",
                attempt,
                last_error,
            )

            if attempt < MAX_ATTEMPTS:
                backoff_seconds = (
                    RETRY_BACKOFF_SECONDS[
                        attempt - 1
                    ]
                )

                await asyncio.sleep(
                    backoff_seconds
                )

    # Do not expose SMTP credentials/internal details
    # through API responses or database error messages.
    sanitized_error = (
        "Email delivery failed after retries."
        if last_error
        else "Unknown email error."
    )

    return EmailSendResult(
        success=False,
        provider_message_id=None,
        error=sanitized_error,
        attempts=MAX_ATTEMPTS,
    )