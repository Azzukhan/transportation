from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "transportation-api"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = Field(
        default="sqlite+aiosqlite:///./db.sqlite3",
        description="Async SQLAlchemy database URL.",
    )

    secret_key: str = Field(default="dev-only-change-me", min_length=16)
    jwt_previous_secret_keys: str = ""
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"
    auth_rate_limit_window_seconds: int = 60
    auth_rate_limit_ip_max_attempts: int = 20
    auth_rate_limit_username_max_attempts: int = 10
    auth_lockout_threshold: int = 5
    auth_lockout_base_seconds: int = 30
    auth_lockout_max_seconds: int = 900
    rate_limit_backend: Literal["memory", "redis"] = "memory"
    redis_url: str = ""
    refresh_token_expire_days: int = 14
    auth_access_cookie_name: str = "access_token"
    auth_refresh_cookie_name: str = "refresh_token"
    auth_csrf_cookie_name: str = "csrf_token"
    auth_cookie_secure: bool = False
    auth_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    auth_cookie_domain: str | None = None
    signature_encryption_enabled: bool = True
    signature_encryption_keys: str = "dev-v1:yOKyzpOfYrQqeMjCOFJ0wTRdG-67M5maVO-9lNvGdDA="
    signature_active_key_id: str = "dev-v1"
    signature_startup_integrity_check_enabled: bool = True
    signature_startup_integrity_fail_on_invalid: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    web_concurrency: int = 2
    use_gunicorn: bool = True
    cors_allowed_origins: str = "http://localhost:8080,http://localhost:5173"
    security_csp: str = (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    )
    security_referrer_policy: str = "no-referrer"
    security_hsts_max_age: int = 63072000
    security_hsts_include_subdomains: bool = True
    security_hsts_preload: bool = True
    rate_limit_window_seconds: int = 60
    rate_limit_global_max_requests: int = 300
    rate_limit_auth_max_requests: int = 30
    rate_limit_upload_max_requests: int = 20
    rate_limit_export_max_requests: int = 40
    max_request_body_bytes: int = 1024 * 1024
    max_auth_body_bytes: int = 16 * 1024
    max_upload_body_bytes: int = 6 * 1024 * 1024
    max_public_request_body_bytes: int = 128 * 1024
    sensitive_export_step_up_required: bool = False
    sensitive_export_step_up_token: str = ""
    audit_hash_key: str = "dev-audit-hash-key-change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        is_production = self.app_env.lower() in {"prod", "production"}
        if self.auth_cookie_samesite == "none" and not self.auth_cookie_secure:
            raise ValueError("AUTH_COOKIE_SECURE must be true when AUTH_COOKIE_SAMESITE=none.")
        if "*" in self.cors_allowed_origins_list:
            raise ValueError("CORS_ALLOWED_ORIGINS cannot contain '*' for this API.")
        if self.access_token_expire_minutes <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be > 0.")
        if self.refresh_token_expire_days <= 0:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be > 0.")
        if self.rate_limit_window_seconds <= 0:
            raise ValueError("RATE_LIMIT_WINDOW_SECONDS must be > 0.")
        if self.rate_limit_global_max_requests <= 0:
            raise ValueError("RATE_LIMIT_GLOBAL_MAX_REQUESTS must be > 0.")
        if self.rate_limit_auth_max_requests <= 0:
            raise ValueError("RATE_LIMIT_AUTH_MAX_REQUESTS must be > 0.")
        if self.rate_limit_upload_max_requests <= 0:
            raise ValueError("RATE_LIMIT_UPLOAD_MAX_REQUESTS must be > 0.")
        if self.rate_limit_export_max_requests <= 0:
            raise ValueError("RATE_LIMIT_EXPORT_MAX_REQUESTS must be > 0.")
        if self.max_request_body_bytes <= 0:
            raise ValueError("MAX_REQUEST_BODY_BYTES must be > 0.")
        if self.max_auth_body_bytes <= 0:
            raise ValueError("MAX_AUTH_BODY_BYTES must be > 0.")
        if self.max_upload_body_bytes <= 0:
            raise ValueError("MAX_UPLOAD_BODY_BYTES must be > 0.")
        if self.max_public_request_body_bytes <= 0:
            raise ValueError("MAX_PUBLIC_REQUEST_BODY_BYTES must be > 0.")
        if self.auth_rate_limit_window_seconds <= 0:
            raise ValueError("AUTH_RATE_LIMIT_WINDOW_SECONDS must be > 0.")
        if self.auth_rate_limit_ip_max_attempts <= 0:
            raise ValueError("AUTH_RATE_LIMIT_IP_MAX_ATTEMPTS must be > 0.")
        if self.auth_rate_limit_username_max_attempts <= 0:
            raise ValueError("AUTH_RATE_LIMIT_USERNAME_MAX_ATTEMPTS must be > 0.")
        if self.auth_lockout_threshold <= 0:
            raise ValueError("AUTH_LOCKOUT_THRESHOLD must be > 0.")
        if self.auth_lockout_base_seconds <= 0:
            raise ValueError("AUTH_LOCKOUT_BASE_SECONDS must be > 0.")
        if self.auth_lockout_max_seconds < self.auth_lockout_base_seconds:
            raise ValueError("AUTH_LOCKOUT_MAX_SECONDS must be >= AUTH_LOCKOUT_BASE_SECONDS.")
        if (
            self.sensitive_export_step_up_required
            and len(self.sensitive_export_step_up_token.strip()) < 24
        ):
            raise ValueError(
                "SENSITIVE_EXPORT_STEP_UP_TOKEN must be at least 24 characters when enabled."
            )
        if (
            self.signature_encryption_enabled
            and self.signature_active_key_id not in self.signature_encryption_keys_map
        ):
            raise ValueError("SIGNATURE_ACTIVE_KEY_ID must exist in SIGNATURE_ENCRYPTION_KEYS.")
        if (
            self.signature_startup_integrity_fail_on_invalid
            and not self.signature_startup_integrity_check_enabled
        ):
            raise ValueError(
                "SIGNATURE_STARTUP_INTEGRITY_CHECK_ENABLED must be true when "
                "SIGNATURE_STARTUP_INTEGRITY_FAIL_ON_INVALID=true."
            )
        if is_production:
            if self.rate_limit_backend != "redis":
                raise ValueError("RATE_LIMIT_BACKEND must be 'redis' in production.")
            if not self.redis_url.strip():
                raise ValueError("REDIS_URL is required when RATE_LIMIT_BACKEND=redis.")
            if self.secret_key in {"change-me", "dev-only-change-me"} or len(self.secret_key) < 32:
                raise ValueError("SECRET_KEY must be strong (>=32 chars) in production.")
            if (
                self.audit_hash_key in {"dev-audit-hash-key-change-me", "change-me"}
                or len(self.audit_hash_key) < 32
            ):
                raise ValueError("AUDIT_HASH_KEY must be strong (>=32 chars) in production.")
            if not self.auth_cookie_secure:
                raise ValueError("AUTH_COOKIE_SECURE must be true in production.")
            if self.debug:
                raise ValueError("DEBUG must be false in production.")
            if self.database_url.startswith("sqlite"):
                raise ValueError("DATABASE_URL cannot use sqlite in production.")
            if not self.signature_encryption_enabled:
                raise ValueError("SIGNATURE_ENCRYPTION_ENABLED must be true in production.")
            if (
                self.signature_encryption_keys.strip()
                == "dev-v1:yOKyzpOfYrQqeMjCOFJ0wTRdG-67M5maVO-9lNvGdDA="
            ):
                raise ValueError("SIGNATURE_ENCRYPTION_KEYS must be replaced in production.")
            for origin in self.cors_allowed_origins_list:
                parsed = urlparse(origin)
                if parsed.hostname in {"localhost", "127.0.0.1"}:
                    raise ValueError("CORS_ALLOWED_ORIGINS cannot include localhost in production.")
                if parsed.scheme != "https":
                    raise ValueError("CORS_ALLOWED_ORIGINS must use https in production.")
        return self

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        origins = [item.strip() for item in self.cors_allowed_origins.split(",")]
        return [item for item in origins if item]

    @property
    def jwt_previous_secret_keys_list(self) -> list[str]:
        values = [item.strip() for item in self.jwt_previous_secret_keys.split(",")]
        return [item for item in values if item]

    @property
    def jwt_decode_secret_keys(self) -> list[str]:
        keys = [self.secret_key, *self.jwt_previous_secret_keys_list]
        unique: list[str] = []
        for key in keys:
            if key not in unique:
                unique.append(key)
        return unique

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"prod", "production"}

    @property
    def signature_encryption_keys_map(self) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for item in self.signature_encryption_keys.split(","):
            token = item.strip()
            if not token:
                continue
            if ":" not in token:
                raise ValueError("SIGNATURE_ENCRYPTION_KEYS must use key_id:base64 format.")
            key_id, key_value = token.split(":", 1)
            key_id = key_id.strip()
            key_value = key_value.strip()
            if not key_id or not key_value:
                raise ValueError("SIGNATURE_ENCRYPTION_KEYS entries cannot be empty.")
            parsed[key_id] = key_value
        return parsed

    @property
    def strict_transport_security_value(self) -> str:
        parts = [f"max-age={self.security_hsts_max_age}"]
        if self.security_hsts_include_subdomains:
            parts.append("includeSubDomains")
        if self.security_hsts_preload:
            parts.append("preload")
        return "; ".join(parts)


@lru_cache
def get_settings() -> Settings:
    return Settings()
