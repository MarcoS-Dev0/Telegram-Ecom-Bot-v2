"""
Application configuration via Pydantic Settings.
Reads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # --- Telegram ---
    BOT_TOKEN: str
    WEBHOOK_BASE_URL: str = "https://yourdomain.com"
    ADMIN_USER_IDS: list[int] = Field(default_factory=list)

    # --- Stripe ---
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_CURRENCY: str = "eur"

    # --- MongoDB ---
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "ecom_bot"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- App Settings ---
    APP_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CART_TTL_HOURS: int = 72
    DEFAULT_LOCALE: str = "en"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    @property
    def webhook_url(self) -> str:
        return f"{self.WEBHOOK_BASE_URL}/api/v1/webhooks/telegram"


settings = Settings()
