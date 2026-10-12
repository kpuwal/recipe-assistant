import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from core.settings import settings

API_KEY_HEADER = "X-Api-Key"

_api_key_header = APIKeyHeader(
    name=API_KEY_HEADER,
    auto_error=False,
    description="Shared API key for the Recipe Assistant app.",
)


def require_api_key(
    provided: str | None = Depends(_api_key_header),
) -> None:
    """Reject the request unless it carries the shared API key.

    Uses a constant-time comparison so the key cannot be recovered by
    timing the endpoint.
    """
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server is missing APP_API_KEY",
        )

    if not provided or not secrets.compare_digest(provided, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": API_KEY_HEADER},
        )