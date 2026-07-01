"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "sqlite:///" + str(BASE_DIR / "database" / "second_brain.db").replace("\\", "/")
    chroma_persist_dir: str = str(BASE_DIR / "embeddings" / "chroma_db")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_content_length: int = 50000

    session_max_age_days: int = 30
    remember_me_days: int = 90

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    uploads_dir: Path = BASE_DIR / "uploads"

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key != "sk-your-openai-api-key-here")


@lru_cache
def get_settings() -> Settings:
    return Settings()
