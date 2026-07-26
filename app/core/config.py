# app/core/config.py
# Loads environment variables from .env and exposes them as a simple config object.

import os
from dotenv import load_dotenv

# Load variables from a .env file into the process environment, if present.
load_dotenv()


class Settings:
    """Application settings pulled from environment variables, with sane defaults."""

    def __init__(self) -> None:
        self.port: int = int(os.getenv("PORT", "8000"))
        self.app_env: str = os.getenv("APP_ENV", "development")


# Singleton settings instance used across the app.
settings = Settings()