"""Integration tests for TradingBot."""
import pytest
from unittest.mock import patch, Mock
from bot import TradingBot


@pytest.fixture
def bot(test_config, mocker):
    """Create bot instance with mocked clients."""
    with patch('bot.load_config', return_value=test_config):
        with patch('bot.validate_config', return_value=(True, [])):
            with patch('bot.PolystrikeClient') as mock_ps:
                with patch('bot.PolymarketClient'):
                    bot = TradingBot()
                    bot.polystrike = mock_ps.return_value
                    bot.polymarket = Mock()
                    return bot


def test_execute_signal_success(test_config, mocker, sample_buy_signal):
    """Test successful signal execution."""
    # Set dry_run=False for this test
    test_config.dry_run = False

    with patch('bot.load_config', return_value=test_config):
        with patch('bot.validate_config', return_value=(True, [])):
            with patch('bot.PolymarketClient') as mock_pm:
                bot = TradingBot()
                bot.polymarket.place_market_buy.return_value = {"order_id": "12345"}

                # Execute signal
                bot.execute_signal(sample_buy_signal, current_exposure=0.20)

                # Verify trade was placed with correct token_id
                bot.polymarket.place_market_buy.assert_called_once_with(
                    token_id="0xjkl012",
                    amount_usd=15.00
                )


def test_execute_signal_no_token_id(bot, sample_buy_signal):
    """Test signal execution when token_id is missing."""
    signal = sample_buy_signal.copy()
    signal["token_id"] = None

    # Execute signal
    bot.execute_signal(signal, current_exposure=0.20)

    # Verify trade was NOT placed
    bot.polymarket.place_market_buy.assert_not_called()


def test_execute_signal_risk_check_fails(bot, sample_buy_signal):
    """Test signal execution when risk check fails."""
    signal = sample_buy_signal.copy()
    signal["edge"] = 0.02  # Below minimum

    # Execute signal
    bot.execute_signal(signal, current_exposure=0.20)

    # Verify trade was NOT placed
    bot.polymarket.place_market_buy.assert_not_called()


def test_dry_run_mode(test_config, mocker):
    """Test bot in dry-run mode doesn't execute trades."""
    test_config.dry_run = True

    with patch('bot.load_config', return_value=test_config):
        with patch('bot.validate_config', return_value=(True, [])):
            bot = TradingBot()
            assert bot.polymarket is None
