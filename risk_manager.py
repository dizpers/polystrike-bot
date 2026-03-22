"""Risk management and position sizing logic."""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class RiskManager:
    """Enforces trading rules and risk limits."""

    def __init__(
        self,
        bankroll: float,
        max_position_size: float,
        min_edge: float,
        stop_loss_pct: float,
        max_portfolio_exposure: float,
        min_confidence: str = "MEDIUM"
    ):
        self.bankroll = bankroll
        self.max_position_size = max_position_size
        self.min_edge = min_edge
        self.stop_loss_pct = stop_loss_pct
        self.max_portfolio_exposure = max_portfolio_exposure
        self.min_confidence = min_confidence

        self.confidence_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

    def should_execute_buy(self, signal: Dict, current_exposure: float) -> tuple[bool, str]:
        """
        Determine if a BUY signal should be executed.

        Args:
            signal: Signal dictionary from Polystrike API
            current_exposure: Current portfolio exposure as fraction of bankroll

        Returns:
            (should_execute, reason)
        """
        # Rule 1: Must be BUY action
        if signal.get("action") != "BUY":
            return False, f"Action is {signal.get('action')}, not BUY"

        # Rule 2: Confidence threshold
        signal_conf = signal.get("confidence", "LOW")
        min_conf_level = self.confidence_levels.get(self.min_confidence, 1)
        signal_conf_level = self.confidence_levels.get(signal_conf, 0)

        if signal_conf_level < min_conf_level:
            return False, f"Confidence {signal_conf} below minimum {self.min_confidence}"

        # Rule 3: Edge threshold
        edge = signal.get("edge", 0)
        if edge < self.min_edge:
            return False, f"Edge {edge:.1%} below minimum {self.min_edge:.1%}"

        # Rule 4: Position size limit
        suggested_bet = signal.get("suggested_bet", 0)
        if suggested_bet > self.max_position_size:
            return False, f"Bet ${suggested_bet:.2f} exceeds max ${self.max_position_size:.2f}"

        # Rule 5: Portfolio exposure limit
        new_exposure = current_exposure + (suggested_bet / self.bankroll)
        if new_exposure > self.max_portfolio_exposure:
            return False, f"Would exceed max exposure ({new_exposure:.1%} > {self.max_portfolio_exposure:.1%})"

        # Rule 6: Model probability threshold (from memory.md §66)
        model_prob = signal.get("model_prob", 0)
        if model_prob < 0.50:
            return False, f"Model probability {model_prob:.1%} below 50% minimum"

        # Rule 7: Moneyness check (avoid bucket boundaries)
        moneyness = signal.get("moneyness", 0)
        if moneyness < 0.2:
            return False, f"Low moneyness {moneyness:.1%} - p50 near bucket edge"

        return True, "All risk checks passed"

    def should_stop_loss(self, position: Dict) -> tuple[bool, str]:
        """
        Determine if a position should be stopped out.

        Args:
            position: Position dictionary from portfolio API

        Returns:
            (should_sell, reason)
        """
        pnl_pct = position.get("pnl_percent", 0)
        model_prob = position.get("analysis", {}).get("win_probability", 0)

        # Smart stop-loss (memory.md §72)
        if pnl_pct <= self.stop_loss_pct:
            if model_prob < 0.50:
                return True, f"Stop-loss triggered: {pnl_pct:.1%} loss and model prob {model_prob:.1%} < 50%"
            else:
                # Model still confident - hold through the dip
                return False, f"Below stop-loss but model prob {model_prob:.1%} >= 50% - holding"

        return False, "No stop-loss trigger"

    def calculate_current_exposure(self, positions: List[Dict]) -> float:
        """
        Calculate current portfolio exposure as fraction of bankroll.

        Args:
            positions: List of active positions

        Returns:
            Exposure fraction (0.0 to 1.0)
        """
        total_deployed = sum(
            float(p.get("cost_basis", 0))
            for p in positions
        )
        return total_deployed / self.bankroll if self.bankroll > 0 else 0.0
