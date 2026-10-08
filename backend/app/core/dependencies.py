from fastapi import Cookie, HTTPException, status

from .config import SESSION_COOKIE_NAME
from ..services.auth_service import auth_service


def get_current_user(route53_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> str:
    username = auth_service.get_username(route53_session)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return username
