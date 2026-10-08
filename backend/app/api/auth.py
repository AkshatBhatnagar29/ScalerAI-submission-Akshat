from fastapi import APIRouter, Cookie, HTTPException, Response, status

from ..core.config import SESSION_COOKIE_NAME
from ..core.security import clear_session_cookie, set_session_cookie
from ..schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
)
from ..services.auth_service import auth_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def current_username(session_cookie: str | None) -> str:
    username = auth_service.get_username(session_cookie)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return username


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response) -> LoginResponse:
    if not auth_service.validate_credentials(payload.username, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password.")

    session_id = auth_service.create_session(payload.username)
    set_session_cookie(response, session_id)
    return LoginResponse(authenticated=True, user=AuthenticatedUser(username=payload.username))


@router.get("/me", response_model=LoginResponse)
def me(route53_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> LoginResponse:
    username = current_username(route53_session)
    return LoginResponse(authenticated=True, user=AuthenticatedUser(username=username))


@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    route53_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> LogoutResponse:
    auth_service.delete_session(route53_session)
    clear_session_cookie(response)
    return LogoutResponse(authenticated=False)
