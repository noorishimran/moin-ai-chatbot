"""
Central application configuration.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    app_url: str = "http://localhost:8000"
    allowed_origins: str = "http://localhost:5173"
    app_secret: str = "change-me-in-env"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/moin_chatbot"
    )

    llm_provider: str = "gemini"
    gemini_api_key: str | None = None
    model_name: str = "gemini-1.5-flash"
    embedding_model: str = "text-embedding-004"

    email_provider: str = "smtp"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    lead_email_to: str = "info@moinsystemsai.com"

    rag_top_k: int = 5
    rag_min_similarity: float = 0.65
    rate_limit_per_minute: int = 30

    @property
    def allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def async_database_url(self) -> str:
        """
        Convert Railway/Postgres URLs to the asyncpg SQLAlchemy format.
        """

        url = self.database_url.strip()

        if url.startswith("postgresql://"):
            return url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        if url.startswith("postgres://"):
            return url.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()