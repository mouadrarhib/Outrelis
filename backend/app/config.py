from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: SecretStr
    session_lifetime_seconds: int = Field(default=86400, ge=300, le=604800)
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    overpass_base_url: str = "https://overpass-api.de/api"
    osm_user_agent: str = "Outrelis/0.1 (development; contact: configure@example.com)"


@lru_cache
def get_settings() -> Settings:
    return Settings()
