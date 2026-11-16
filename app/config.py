"""EduLingua AI — Application Configuration.

Central configuration module using pydantic-settings.
All settings are loaded from environment variables.
"""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ULTIMATE = "ultimate"


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Telegram ---
    telegram_bot_token: SecretStr = Field(..., description="Telegram Bot API token")
    webhook_base_url: str = Field(
        default="",
        description="Public HTTPS URL for webhook (auto-detected on Railway if empty)",
    )
    webhook_secret: SecretStr = Field(..., description="Webhook secret token")
    webhook_path: str = Field("/telegram/webhook", description="Webhook endpoint path")

    # --- Database ---
    database_url: str = Field(
        "postgresql+asyncpg://edulingua:edulingua_password@localhost:5432/edulingua"
    )
    database_echo: bool = Field(False)
    database_pool_size: int = Field(10)
    database_max_overflow: int = Field(5)

    # --- Redis ---
    redis_url: str = Field("redis://localhost:6379/0")
    redis_queue_db: int = Field(1)
    redis_cache_ttl: int = Field(300)

    # --- AI Provider ---
    gemini_api_key: SecretStr | None = Field(None, description="Google Gemini API key")
    gemini_model: str = Field("gemini-2.0-flash")
    gemini_vision_model: str = Field("gemini-2.0-flash")
    ai_max_tokens: int = Field(4096)
    ai_temperature: float = Field(0.7)
    ai_request_timeout: int = Field(60)
    ai_max_context_messages: int = Field(20)

    # --- Rate Limiting ---
    rate_limit_messages_per_minute: int = Field(30)
    rate_limit_ai_requests_per_hour_free: int = Field(20)
    rate_limit_ai_requests_per_hour_pro: int = Field(100)
    rate_limit_ai_requests_per_hour_ultimate: int = Field(500)

    # --- Admin ---
    admin_secret_key: SecretStr = Field("change-me-in-production")
    admin_username: str = Field("admin")
    admin_password_hash: str = Field("")
    admin_token_expire_minutes: int = Field(60)

    # --- Application ---
    app_env: Environment = Field(Environment.PRODUCTION)
    app_debug: bool = Field(False)
    app_log_level: str = Field("INFO")
    app_host: str = Field("0.0.0.0")
    app_port: int = Field(8000, validation_alias=AliasChoices("PORT", "APP_PORT"))
    workers_count: int = Field(1)

    # --- Premium Limits ---
    free_ai_daily_limit: int = Field(20)
    pro_ai_daily_limit: int = Field(100)
    ultimate_ai_daily_limit: int = Field(500)
    free_daily_tasks: int = Field(3)
    pro_daily_tasks: int = Field(10)
    ultimate_daily_tasks: int = Field(0)  # 0 = unlimited

    # --- Payments ---
    payment_provider_token: str | None = Field(None)
    payment_currency: str = Field("USD")

    @property
    def webhook_url(self) -> str:
        """Full webhook URL."""
        if not self.webhook_base_url:
            return ""
        base = self.webhook_base_url.rstrip("/")
        path = self.webhook_path.lstrip("/")
        return f"{base}/{path}"

    @property
    def is_debug(self) -> bool:
        return self.app_debug or self.app_env == Environment.DEVELOPMENT

    @property
    def has_gemini_key(self) -> bool:
        return self.gemini_api_key is not None and len(
            self.gemini_api_key.get_secret_value()
        ) > 0

    @property
    def has_payment_provider(self) -> bool:
        return bool(self.payment_provider_token)

    def get_ai_daily_limit(self, tier: SubscriptionTier) -> int:
        """Get AI request daily limit for a subscription tier."""
        limits = {
            SubscriptionTier.FREE: self.free_ai_daily_limit,
            SubscriptionTier.PRO: self.pro_ai_daily_limit,
            SubscriptionTier.ULTIMATE: self.ultimate_ai_daily_limit,
        }
        return limits.get(tier, self.free_ai_daily_limit)

    def get_daily_task_limit(self, tier: SubscriptionTier) -> int:
        """Get daily task limit for a subscription tier. 0 = unlimited."""
        limits = {
            SubscriptionTier.FREE: self.free_daily_tasks,
            SubscriptionTier.PRO: self.pro_daily_tasks,
            SubscriptionTier.ULTIMATE: self.ultimate_daily_tasks,
        }
        return limits.get(tier, self.free_daily_tasks)

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("postgres://"):
                return v_clean.replace("postgres://", "postgresql+asyncpg://", 1)
            if v_clean.startswith("postgresql://") and not v_clean.startswith("postgresql+asyncpg://"):
                return v_clean.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("webhook_base_url", mode="before")
    @classmethod
    def validate_webhook_url(cls, v: str | None) -> str:
        if not v:
            # Auto-detect Railway public domain if available
            railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("RAILWAY_STATIC_URL")
            if railway_domain:
                return f"https://{railway_domain.strip('/')}"
            return ""
        v = v.strip()
        if not v.startswith("http://") and not v.startswith("https://"):
            return f"https://{v}"
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
