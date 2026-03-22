"""Unit tests for RiskManager."""
import pytest


def test_should_execute_buy_high_confidence(risk_manager, sample_buy_signal):
    """Test BUY signal with HIGH confidence passes all checks."""
    should_execute, reason = risk_manager.should_execute_buy(
        sample_buy_signal,
        current_exposure=0.20
    )
    assert should_execute is True


def test_should_execute_buy_insufficient_edge(risk_manager, sample_buy_signal):
    """Test BUY signal with edge below threshold is rejected."""
    signal = sample_buy_signal.copy()
    signal["edge"] = 0.02  # Below min_edge of 0.05

    should_execute, reason = risk_manager.should_execute_buy(signal, 0.20)
    assert should_execute is False
    assert "edge" in reason.lower()


def test_should_execute_buy_position_too_large(risk_manager, sample_buy_signal):
    """Test BUY signal exceeding max position size is rejected."""
    signal = sample_buy_signal.copy()
    signal["suggested_bet"] = 50.0  # Exceeds max_position_size of 30.0

    should_execute, reason = risk_manager.should_execute_buy(signal, 0.20)
    assert should_execute is False
    assert "exceeds max" in reason.lower()


def test_should_execute_buy_portfolio_exposure_limit(risk_manager, sample_buy_signal):
    """Test BUY signal rejected when portfolio exposure too high."""
    should_execute, reason = risk_manager.should_execute_buy(
        sample_buy_signal,
        current_exposure=0.75  # Already at 75%, adding 15% would exceed 80%
    )
    assert should_execute is False
    assert "exposure" in reason.lower()


def test_should_stop_loss_triggered(risk_manager, sample_position):
    """Test stop-loss triggers at -30% loss with low model prob."""
    position = sample_position.copy()
    position["pnl_percent"] = -0.31  # -31% loss
    position["analysis"]["win_probability"] = 0.45  # Model not confident

    should_sell, reason = risk_manager.should_stop_loss(position)
    assert should_sell is True
    assert "stop-loss" in reason.lower()


def test_should_stop_loss_model_override(risk_manager, sample_position):
    """Test stop-loss NOT triggered when model prob > 50%."""
    position = sample_position.copy()
    position["pnl_percent"] = -0.35  # -35% loss
    position["analysis"]["win_probability"] = 0.55  # Model still bullish

    should_sell, reason = risk_manager.should_stop_loss(position)
    assert should_sell is False  # Model override prevents sell


def test_calculate_current_exposure(risk_manager):
    """Test portfolio exposure calculation."""
    positions = [
        {"cost_basis": 15.0},
        {"cost_basis": 20.0},
        {"cost_basis": 10.0}
    ]

    exposure = risk_manager.calculate_current_exposure(positions)
    assert exposure == 0.45  # 45/100 = 45%
