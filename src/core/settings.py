from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "NEXUS OS"
    VERSION: str = "0.1.0"
    AUTHOR: str = "Haseeb"

    DEBUG: bool = True

    DATABASE_NAME: str = "nexus_os"
    DATABASE_URL: str

    AI_ENGINE: str = "Not Initialized"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]
