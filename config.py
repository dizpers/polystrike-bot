"""Configuration management for Polystrike Trading Bot."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
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

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        populate_by_name=True
    )


def load_config() -> Config:
    """Load configuration from .env file."""
    return Config()


def validate_config(config: Config) -> tuple[bool, list[str]]:
    """
    Validate configuration and return (is_valid, errors).

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Validate Polystrike API
    if not config.polystrike_api_key:
        errors.append("POLYSTRIKE_API_KEY is required")
    elif not config.polystrike_api_key.startswith("ps_pro_"):
        errors.append("POLYSTRIKE_API_KEY must start with 'ps_pro_'")

    # Validate wallet (only if not dry-run)
    if not config.dry_run:
        if not config.wallet_private_key:
            errors.append("WALLET_PRIVATE_KEY is required for live trading")
        elif not config.wallet_private_key.startswith("0x"):
            errors.append("WALLET_PRIVATE_KEY must start with '0x'")
        elif len(config.wallet_private_key) != 66:
            errors.append("WALLET_PRIVATE_KEY must be 66 characters (0x + 64 hex)")

        if not config.wallet_address:
            errors.append("WALLET_ADDRESS is required for live trading")
        elif not config.wallet_address.startswith("0x"):
            errors.append("WALLET_ADDRESS must start with '0x'")
        elif len(config.wallet_address) != 42:
            errors.append("WALLET_ADDRESS must be 42 characters (0x + 40 hex)")

    # Validate trading parameters
    if config.bankroll <= 0:
        errors.append("BANKROLL must be positive")

    if config.max_position_size > config.bankroll:
        errors.append("MAX_POSITION_SIZE cannot exceed BANKROLL")

    if not 0 < config.min_edge < 1:
        errors.append("MIN_EDGE must be between 0 and 1")

    if not -1 < config.stop_loss_pct < 0:
        errors.append("STOP_LOSS_PCT must be negative (e.g., -0.30)")

    if config.min_confidence not in ["LOW", "MEDIUM", "HIGH"]:
        errors.append("MIN_CONFIDENCE must be LOW, MEDIUM, or HIGH")

    return len(errors) == 0, errors
