from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=256)


class AuthenticatedUser(BaseModel):
    username: str


class LoginResponse(BaseModel):
    authenticated: bool
    user: AuthenticatedUser


class LogoutResponse(BaseModel):
    authenticated: bool
