import secrets

from fastapi import Response

from .config import COOKIE_SAMESITE, COOKIE_SECURE, SESSION_COOKIE_NAME, SESSION_MAX_AGE


def generate_session_id() -> str:
    """Return an opaque, cryptographically random session identifier."""
    return secrets.token_urlsafe(32)


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
