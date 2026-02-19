from pydantic import BaseModel


class LoginInput(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    username: str | None = None


class RefreshTokenInput(BaseModel):
    refresh_token: str


class MeResponse(BaseModel):
    username: str
