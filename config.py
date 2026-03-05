"""Configuration management for Polystrike Trading Bot."""
import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Bot configuration from environment variables."""

    # Polystrike API
    polystrike_api_key: str = Field(..., alias="POLYSTRIKE_API_KEY")
    polystrike_api_url: str = Field(
        default="https://polystrike.xyz/api/v1",
        alias="POLYSTRIKE_API_URL"
    )

    # Polymarket Wallet
    wallet_private_key: str = Field(..., alias="WALLET_PRIVATE_KEY")
    wallet_address: str = Field(..., alias="WALLET_ADDRESS")
    chain_id: int = Field(default=137, alias="CHAIN_ID")

    # Trading Parameters
    bankroll: float = Field(default=100.0, alias="BANKROLL")
    max_position_size: float = Field(default=30.0, alias="MAX_POSITION_SIZE")
    min_edge: float = Field(default=0.05, alias="MIN_EDGE")
    stop_loss_pct: float = Field(default=-0.30, alias="STOP_LOSS_PCT")
    max_portfolio_exposure: float = Field(default=0.80, alias="MAX_PORTFOLIO_EXPOSURE")

    # Risk Management
    require_approval: bool = Field(default=False, alias="REQUIRE_APPROVAL")
    dry_run: bool = Field(default=False, alias="DRY_RUN")
    min_confidence: str = Field(default="MEDIUM", alias="MIN_CONFIDENCE")

    # Polling
    poll_interval_seconds: int = Field(default=300, alias="POLL_INTERVAL_SECONDS")

    # Telegram (Optional)
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, alias="TELEGRAM_CHAT_ID")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="trades.log", alias="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config() -> Config:
    """Load configuration from .env file."""
    return Config()
