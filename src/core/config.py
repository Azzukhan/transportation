from functools import lru_cache

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
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"
    predefined_users: str = Field(
        default="admin:secret",
        description="Comma-separated username:password pairs for auth without a users table.",
    )
    host: str = "0.0.0.0"
    port: int = 8000
    web_concurrency: int = 2
    use_gunicorn: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        is_production = self.app_env.lower() in {"prod", "production"}
        if is_production and self.secret_key in {"change-me", "dev-only-change-me"}:
            raise ValueError("SECRET_KEY must be set from environment in non-debug mode.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
