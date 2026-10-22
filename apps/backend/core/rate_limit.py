import hashlib
import secrets
import threading
import time

from collections import defaultdict, deque
from math import ceil

from fastapi import HTTPException, Request

from core.settings import settings


class SlidingWindowLimiter:
    """In-memory sliding-window rate limiter.

    State is per process. Cloud Run may run multiple instances, so the real
    limit is per instance; the goal is to stop a leaked key from causing
    unbounded Groq or ingestion costs, not exact global accounting.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._events = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str) -> float:
        """Record a request and return seconds to wait, or 0 if allowed."""
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            events = self._events[key]

            while events and events[0] <= cutoff:
                events.popleft()

            if len(events) >= self.max_requests:
                return max(0.0, events[0] + self.window_seconds - now)

            events.append(now)
            return 0.0


def rate_limit(scope: str, max_requests: int, window_seconds: int):
    limiter = SlidingWindowLimiter(max_requests, window_seconds)

    async def dependency(request: Request) -> None:
        provided = request.headers.get("X-Api-Key", "").encode("utf-8")
        expected = settings.api_key.encode("utf-8")

        # Invalid keys are rejected by require_api_key. Do not let them consume
        # the bucket for the real key, and do not create state for them.
        if not provided or not secrets.compare_digest(provided, expected):
            return

        # There is one shared key. Hashing the configured key (rather than the
        # request header) keeps the limiter state bounded.
        key = f"{scope}:{hashlib.sha256(expected).hexdigest()[:16]}"
        retry_after = limiter.hit(key)

        if retry_after > 0:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(max(1, ceil(retry_after)))},
            )

    return dependency
