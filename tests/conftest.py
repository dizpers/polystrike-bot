"""Shared test fixtures."""
import pytest
from unittest.mock import Mock
from config import Config
from risk_manager import RiskManager


@pytest.fixture
def test_config():
    """Test configuration with safe defaults."""
    return Config(
        polystrike_api_url="https://polystrike.xyz/api/v1",
        polystrike_api_key="ps_pro_test_key",
        wallet_private_key="0x" + "0" * 64,
        wallet_address="0x1234567890123456789012345678901234567890",
        bankroll=100.0,
        max_position_size=30.0,
        min_edge=0.05,
        stop_loss_pct=-0.30,
        max_portfolio_exposure=0.80,
        min_confidence="MEDIUM",
        poll_interval_seconds=300,
        dry_run=True,
        require_approval=False,
        chain_id=137
    )


@pytest.fixture
def risk_manager(test_config):
    """Real risk manager instance for testing."""
    return RiskManager(
        bankroll=test_config.bankroll,
        max_position_size=test_config.max_position_size,
        min_edge=test_config.min_edge,
        stop_loss_pct=test_config.stop_loss_pct,
        max_portfolio_exposure=test_config.max_portfolio_exposure,
        min_confidence=test_config.min_confidence
    )


@pytest.fixture
def sample_buy_signal():
    """Sample BUY signal from Polystrike API."""
    return {
        "event_id": 236151,
        "bucket": "65-89",
        "token_id": "0xjkl012",
        "action": "BUY",
        "model_prob": 0.72,
        "market_price": 0.45,
        "edge": 0.27,
        "ev": 0.60,
        "kelly_fraction": 0.15,
        "suggested_bet": 15.00,
        "confidence": "HIGH",
        "moneyness": 0.5
    }


@pytest.fixture
def sample_skip_signal():
    """Sample SKIP signal."""
    return {
        "event_id": 236151,
        "bucket": "90-114",
        "token_id": "0xmno345",
        "action": "SKIP",
        "model_prob": 0.08,
        "market_price": 0.12,
        "edge": -0.04,
        "ev": -0.33,
        "kelly_fraction": 0.00,
        "suggested_bet": 0.00,
        "confidence": "LOW",
        "moneyness": 0.0,
        "reasons": ["Model prob 8% < 50% minimum"]
    }


@pytest.fixture
def sample_position():
    """Sample position for stop-loss testing."""
    return {
        "event_id": 236151,
        "bucket": "65-89",
        "tokens": 33.3,
        "avg_price": 0.45,
        "cost_basis": 15.0,
        "current_price": 0.32,
        "current_value": 10.66,
        "pnl": -4.34,
        "pnl_percent": -0.29,
        "analysis": {
            "win_probability": 0.48,
            "edge": -0.02
        }
    }
