import secrets
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import Select, select

from src.api.deps import CurrentAdminDep, DBSessionDep, SettingsDep
from src.core.audit import audit_event
from src.core.auth import authenticate_admin_user, create_access_token
from src.core.auth_protection import AuthAttemptGuard
from src.core.refresh_tokens import (
    RefreshTokenReuseDetected,
    issue_refresh_token,
    revoke_all_refresh_tokens_for_user,
    rotate_refresh_token,
)
from src.models.admin_user import AdminUser
from src.schemas.auth import LoginInput, MeResponse, RefreshTokenInput, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
    settings: SettingsDep,
) -> None:
    response.set_cookie(
        key=settings.auth_access_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        domain=settings.auth_cookie_domain,
    )
    response.set_cookie(
        key=settings.auth_refresh_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        domain=settings.auth_cookie_domain,
    )
    response.set_cookie(
        key=settings.auth_csrf_cookie_name,
        value=csrf_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=False,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/",
        domain=settings.auth_cookie_domain,
    )


def _clear_auth_cookies(response: Response, settings: SettingsDep) -> None:
    for cookie_name in [
        settings.auth_access_cookie_name,
        settings.auth_refresh_cookie_name,
        settings.auth_csrf_cookie_name,
    ]:
        response.delete_cookie(
            key=cookie_name,
            path="/",
            domain=settings.auth_cookie_domain,
        )


@router.post("/token", response_model=TokenResponse)
async def issue_token(
    payload: LoginInput,
    request: Request,
    response: Response,
    settings: SettingsDep,
    session: DBSessionDep,
) -> TokenResponse:
    guard = request.app.state.auth_attempt_guard
    if not isinstance(guard, AuthAttemptGuard):
        raise HTTPException(status_code=500, detail="Auth protection is not configured")

    forwarded_for = request.headers.get("X-Forwarded-For", "")
    client_ip = (
        forwarded_for.split(",")[0].strip()
        if forwarded_for.strip()
        else (request.client.host if request.client else "unknown")
    )
    decision = await guard.check_attempt(client_ip=client_ip, username=payload.username)
    if not decision.allowed:
        await audit_event(
            request,
            actor=payload.username,
            tenant_id=None,
            resource="auth",
            action="token_issue_attempt",
            outcome="denied_rate_limit",
            metadata={"client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"{decision.reason} Try again in {decision.retry_after_seconds} seconds."
                if decision.retry_after_seconds is not None
                else (decision.reason or "Too many login attempts.")
            ),
            headers=(
                {"Retry-After": str(decision.retry_after_seconds)}
                if decision.retry_after_seconds is not None
                else None
            ),
        )

    if not await authenticate_admin_user(session, payload.username, payload.password):
        lockout_seconds = await guard.register_failure(payload.username)
        if lockout_seconds is not None:
            await audit_event(
                request,
                actor=payload.username,
                tenant_id=None,
                resource="auth",
                action="token_issue_attempt",
                outcome="denied_lockout",
                metadata={"client_ip": client_ip, "retry_after_seconds": lockout_seconds},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts for this username. Try again in {lockout_seconds} seconds.",
                headers={"Retry-After": str(lockout_seconds)},
            )
        await audit_event(
            request,
            actor=payload.username,
            tenant_id=None,
            resource="auth",
            action="token_issue_attempt",
            outcome="failed_invalid_credentials",
            metadata={"client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    await guard.register_success(payload.username)
    user_stmt: Select[tuple[AdminUser]] = select(AdminUser).where(
        AdminUser.username == payload.username
    )
    user_result = await session.execute(user_stmt)
    admin_user = user_result.scalar_one_or_none()
    if admin_user is None:
        await audit_event(
            request,
            actor=payload.username,
            tenant_id=None,
            resource="auth",
            action="token_issue_attempt",
            outcome="failed_user_not_found",
            metadata={"client_ip": client_ip},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )

    access_token = create_access_token(
        subject=payload.username,
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_version=admin_user.token_version,
    )
    refresh_token = await issue_refresh_token(session, admin_user=admin_user, settings=settings)
    csrf_token = secrets.token_urlsafe(24)
    _set_auth_cookies(
        response,
        access_token=access_token,
        refresh_token=refresh_token,
        csrf_token=csrf_token,
        settings=settings,
    )
    await audit_event(
        request,
        actor=admin_user.username,
        tenant_id=admin_user.transport_company_id,
        resource="auth",
        action="token_issued",
        metadata={"client_ip": client_ip},
    )
    return TokenResponse(username=admin_user.username)


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    settings: SettingsDep,
    session: DBSessionDep,
    payload: RefreshTokenInput | None = None,
) -> TokenResponse:
    provided_refresh_token = payload.refresh_token if payload is not None else None
    if not provided_refresh_token:
        provided_refresh_token = request.cookies.get(settings.auth_refresh_cookie_name)
    if not provided_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
        )
    try:
        admin_user, new_refresh_token = await rotate_refresh_token(
            session,
            provided_token=provided_refresh_token,
            settings=settings,
        )
    except RefreshTokenReuseDetected as exc:
        await audit_event(
            request,
            actor="unknown",
            tenant_id=None,
            resource="auth",
            action="token_refresh",
            outcome="failed_reuse_detected",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        await audit_event(
            request,
            actor="unknown",
            tenant_id=None,
            resource="auth",
            action="token_refresh",
            outcome="failed_invalid_token",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token = create_access_token(
        subject=admin_user.username,
        settings=settings,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_version=admin_user.token_version,
    )
    csrf_token = secrets.token_urlsafe(24)
    _set_auth_cookies(
        response,
        access_token=access_token,
        refresh_token=new_refresh_token,
        csrf_token=csrf_token,
        settings=settings,
    )
    await audit_event(
        request,
        actor=admin_user.username,
        tenant_id=admin_user.transport_company_id,
        resource="auth",
        action="token_refreshed",
    )
    return TokenResponse(username=admin_user.username)


@router.get("/me", response_model=MeResponse)
async def get_me(
    request: Request,
    current_admin: CurrentAdminDep,
) -> MeResponse:
    await audit_event(
        request,
        actor=current_admin.username,
        tenant_id=current_admin.transport_company_id,
        resource="auth",
        action="session_me_read",
    )
    return MeResponse(username=current_admin.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_admin: CurrentAdminDep,
    response: Response,
    settings: SettingsDep,
    session: DBSessionDep,
) -> None:
    stmt: Select[tuple[AdminUser]] = select(AdminUser).where(
        AdminUser.username == current_admin.username
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        _clear_auth_cookies(response, settings)
        return None
    user.token_version += 1
    await session.flush()
    await revoke_all_refresh_tokens_for_user(session, admin_user_id=user.id)
    _clear_auth_cookies(response, settings)
    await audit_event(
        request,
        actor=user.username,
        tenant_id=user.transport_company_id,
        resource="auth",
        action="logout",
    )
    return None
