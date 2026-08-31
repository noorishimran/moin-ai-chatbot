"""
6.7 Rate limiting.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, Request

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 15

_hits: dict[str, list[float]] = defaultdict(list)


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


async def enforce_rate_limit(request: Request) -> None:
    key = _client_key(request)
    now = time.monotonic()

    _hits[key] = [t for t in _hits[key] if now - t < WINDOW_SECONDS]

    if len(_hits[key]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down and try again shortly.")

    _hits[key].append(now)