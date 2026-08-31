"""
6.11 Structured logging.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs one line per request: request ID, method, path, status, and
    latency. Does NOT log request/response bodies (may contain lead
    PII or model output) — only shape/metadata.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.monotonic()

        response = await call_next(request)

        duration_ms = round((time.monotonic() - start) * 1000, 1)
        logger = logging.getLogger("moin_ai.request")
        logger.info(
            f"request_id={request_id} {request.method} {request.url.path} "
            f"status={response.status_code} duration_ms={duration_ms}"
        )
        response.headers["X-Request-ID"] = request_id
        return response