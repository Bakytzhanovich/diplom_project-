from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://acs_user:secret@localhost:5432/acs_db"

    # Redis
    redis_url: str = "redis://:secret@localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change_me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # MFA / Email
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = "noreply@example.com"
    smtp_password: str = ""
    mfa_otp_expire_seconds: int = 300

    # Security
    cors_origins: str = "http://localhost:3000"
    login_rate_limit: int = 5

    # App
    app_env: str = "development"
    app_secret: str = "change_me_secret"

    # Working Hours (UTC, ABAC)
    work_hour_start: int = 8
    work_hour_end: int = 20

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
