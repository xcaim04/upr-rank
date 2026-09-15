"""Application configuration made available through environment variables.

Values come from environment variables or a ``.env`` file. Never hardcode
secrets: override them per environment (local, docker, production).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the UPR-RANK backend service."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "UPR-RANK Backend"
    debug: bool = False

    database_url: str = (
        "postgresql+psycopg2://upr_rank:upr_rank@localhost:5432/upr_rank"
    )
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7


settings = Settings()
