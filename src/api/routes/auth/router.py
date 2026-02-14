from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from src.api.deps import SettingsDep
from src.core.auth import authenticate_predefined_user, create_access_token
from src.schemas.auth import LoginInput, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def issue_token(
    payload: LoginInput,
    settings: SettingsDep,
) -> TokenResponse:
    if not authenticate_predefined_user(payload.username, payload.password, settings):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        subject=payload.username,
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenResponse(access_token=access_token)
