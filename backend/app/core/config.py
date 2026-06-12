from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI-Powered Healthcare Prediction & Resource Management System"
    database_url: str = Field(default="sqlite:///./hospital.db", alias="DATABASE_URL")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: list[str] | str = Field(default_factory=lambda: ["http://localhost:5173"], alias="CORS_ORIGINS")

    def model_post_init(self, __context: object) -> None:
        if isinstance(self.cors_origins, str):
            self.cors_origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

