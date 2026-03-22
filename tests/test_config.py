"""Test configuration validation."""
import pytest
from config import Config, validate_config


def test_validate_config_valid():
    """Test validation passes for valid config."""
    config = Config(
        polystrike_api_key="ps_pro_test123",
        polystrike_api_url="https://polystrike.xyz/api/v1",
        wallet_private_key="0x" + "a" * 64,
        wallet_address="0x" + "b" * 40,
        bankroll=100.0,
        max_position_size=30.0,
        min_edge=0.05,
        stop_loss_pct=-0.30,
        max_portfolio_exposure=0.80,
        min_confidence="MEDIUM",
        dry_run=False
    )

    is_valid, errors = validate_config(config)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_config_invalid_api_key():
    """Test validation fails for invalid API key."""
    config = Config(
        polystrike_api_key="invalid_key",  # Wrong prefix
        wallet_private_key="0x" + "a" * 64,
        wallet_address="0x" + "b" * 40,
        bankroll=100.0,
        dry_run=False
    )

    is_valid, errors = validate_config(config)
    assert is_valid is False
    assert any("ps_pro_" in err for err in errors)


def test_validate_config_dry_run_skips_wallet():
    """Test validation skips wallet checks in dry-run mode."""
    config = Config(
        polystrike_api_key="ps_pro_test123",
        wallet_private_key="invalid",  # Invalid but should be ignored
        wallet_address="invalid",  # Invalid but should be ignored
        bankroll=100.0,
        dry_run=True  # Dry run mode
    )

    is_valid, errors = validate_config(config)
    # Should only fail on API key if at all, not wallet
    wallet_errors = [e for e in errors if "WALLET" in e]
    assert len(wallet_errors) == 0


def test_validate_config_invalid_wallet_private_key():
    """Test validation fails for invalid private key."""
    config = Config(
        polystrike_api_key="ps_pro_test123",
        wallet_private_key="invalid",  # Missing 0x and wrong length
        wallet_address="0x" + "b" * 40,
        bankroll=100.0,
        dry_run=False
    )

    is_valid, errors = validate_config(config)
    assert is_valid is False
    assert any("WALLET_PRIVATE_KEY" in err for err in errors)


def test_validate_config_position_size_exceeds_bankroll():
    """Test validation fails when position size > bankroll."""
    config = Config(
        polystrike_api_key="ps_pro_test123",
        wallet_private_key="0x" + "a" * 64,
        wallet_address="0x" + "b" * 40,
        bankroll=100.0,
        max_position_size=150.0,  # Exceeds bankroll
        dry_run=False
    )

    is_valid, errors = validate_config(config)
    assert is_valid is False
    assert any("MAX_POSITION_SIZE" in err and "exceed" in err for err in errors)
