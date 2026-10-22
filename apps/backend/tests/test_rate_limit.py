from unittest.mock import patch

import pytest
from pydantic import ValidationError

from core.rate_limit import SlidingWindowLimiter
from models.models import ChatRequest


def test_limiter_allows_requests_under_limit():
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=60)

    with patch("core.rate_limit.time.monotonic", return_value=100.0):
        assert limiter.hit("key") == 0.0
        assert limiter.hit("key") == 0.0


def test_limiter_blocks_until_window_expires():
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=60)

    with patch("core.rate_limit.time.monotonic", return_value=100.0):
        limiter.hit("key")
        limiter.hit("key")

    with patch("core.rate_limit.time.monotonic", return_value=102.0):
        retry_after = limiter.hit("key")

    assert retry_after == pytest.approx(58.0)

    with patch("core.rate_limit.time.monotonic", return_value=161.0):
        assert limiter.hit("key") == 0.0


def test_limiter_keeps_separate_buckets():
    limiter = SlidingWindowLimiter(max_requests=1, window_seconds=60)

    with patch("core.rate_limit.time.monotonic", return_value=100.0):
        assert limiter.hit("one") == 0.0
        assert limiter.hit("two") == 0.0


def test_chat_request_rejects_empty_and_oversized_messages():
    with pytest.raises(ValidationError):
        ChatRequest(message="")

    with pytest.raises(ValidationError):
        ChatRequest(message="x" * 2001)


def test_chat_request_accepts_max_length_message():
    request = ChatRequest(message="x" * 2000)

    assert len(request.message) == 2000
