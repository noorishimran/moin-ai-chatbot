"""
6.1 Email service adapter using Mailtrap HTTP API.

Email delivery logic is kept isolated here so the rest of the
application does not depend on SMTP-specific implementation details.
"""

import asyncio
import logging

import httpx

from app.core.config import get_settings


logger = logging.getLogger("moin_ai.email")
settings = get_settings()


MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = [2, 5]
REQUEST_TIMEOUT_SECONDS = 10


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
    Send one email using the Mailtrap Sandbox HTTP API.

    Raises an exception on failure.
    Returns a provider message id on success.
    """

    if not settings.mailtrap_api_token:
        raise RuntimeError(
            "MAILTRAP_API_TOKEN is not configured."
        )

    if not settings.mailtrap_sandbox_id:
        raise RuntimeError(
            "MAILTRAP_SANDBOX_ID is not configured."
        )

    url = (
        "https://sandbox.api.mailtrap.io/api/send/"
        f"{settings.mailtrap_sandbox_id}"
    )

    headers = {
        "Authorization": (
            f"Bearer {settings.mailtrap_api_token}"
        ),
        "Content-Type": "application/json",
    }

    payload = {
        "from": {
            "email": "hello@moinsystemsai.com",
            "name": "MoinSystems AI Chatbot",
        },
        "to": [
            {
                "email": to_addr,
            }
        ],
        "subject": subject,
        "text": body,
        "category": "Lead Notification",
    }

    timeout = httpx.Timeout(
        REQUEST_TIMEOUT_SECONDS
    )

    async with httpx.AsyncClient(
        timeout=timeout
    ) as client:
        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

    response.raise_for_status()

    data = response.json()

    message_ids = data.get("message_ids")

    if (
        isinstance(message_ids, list)
        and message_ids
    ):
        return str(message_ids[0])

    return "sent"


async def send_lead_notification(
    subject: str,
    body: str,
) -> EmailSendResult:
    """
    Send the internal lead notification through
    the Mailtrap HTTP API.

    Retries temporary failures up to MAX_ATTEMPTS.
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
                await asyncio.sleep(
                    RETRY_BACKOFF_SECONDS[
                        attempt - 1
                    ]
                )

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