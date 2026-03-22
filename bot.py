"""Main trading bot loop."""
import logging
import time
import sys
from datetime import datetime

from config import load_config, validate_config
from polystrike_client import PolystrikeClient
from polymarket_client import PolymarketClient
from risk_manager import RiskManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('trades.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Automated trading bot for Polymarket using Polystrike signals."""

    def __init__(self):
        self.config = load_config()

        # Validate configuration
        is_valid, errors = validate_config(self.config)
        if not is_valid:
            logger.error("❌ Configuration errors:")
            for error in errors:
                logger.error(f"   - {error}")
            sys.exit(1)

        logger.info("✅ Configuration validated")

        # Initialize clients
        self.polystrike = PolystrikeClient(
            api_url=self.config.polystrike_api_url,
            api_key=self.config.polystrike_api_key
        )

        if not self.config.dry_run:
            self.polymarket = PolymarketClient(
                private_key=self.config.wallet_private_key,
                chain_id=self.config.chain_id
            )
        else:
            self.polymarket = None
            logger.info("🔧 DRY RUN MODE - No real trades will be executed")

        # Initialize risk manager
        self.risk_manager = RiskManager(
            bankroll=self.config.bankroll,
            max_position_size=self.config.max_position_size,
            min_edge=self.config.min_edge,
            stop_loss_pct=self.config.stop_loss_pct,
            max_portfolio_exposure=self.config.max_portfolio_exposure,
            min_confidence=self.config.min_confidence
        )

    def run(self):
        """Main bot loop."""
        logger.info("🚀 Polystrike Trading Bot started")
        logger.info(f"Bankroll: ${self.config.bankroll:.2f}")
        logger.info(f"Max position: ${self.config.max_position_size:.2f}")
        logger.info(f"Min edge: {self.config.min_edge:.1%}")
        logger.info(f"Poll interval: {self.config.poll_interval_seconds}s")

        while True:
            try:
                self.execute_cycle()
                time.sleep(self.config.poll_interval_seconds)
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retrying

    def execute_cycle(self):
        """Execute one trading cycle."""
        logger.info("🔍 Fetching signals from Polystrike API...")

        # Get current portfolio state
        portfolio = self.polystrike.get_portfolio(self.config.wallet_address)
        positions = portfolio.get("positions", [])

        current_exposure = self.risk_manager.calculate_current_exposure(positions)
        logger.info(f"📊 Current exposure: {current_exposure:.1%} of bankroll")

        # Check for stop-loss triggers
        self.check_stop_losses(positions)

        # Get new signals
        signals = self.polystrike.get_signals(self.config.bankroll)

        # Filter for BUY signals only
        buy_signals = [s for s in signals if s.get("action") == "BUY"]

        if not buy_signals:
            logger.info("✅ No BUY signals at this time")
            return

        logger.info(f"💰 Found {len(buy_signals)} BUY signal(s)")

        # Execute signals
        for signal in buy_signals:
            self.execute_signal(signal, current_exposure)

    def execute_signal(self, signal: dict, current_exposure: float):
        """Execute a single BUY signal."""
        bucket = signal.get("bucket")
        event_id = signal.get("event_id")
        token_id = signal.get("token_id")  # Get from signal directly

        # Risk check
        should_execute, reason = self.risk_manager.should_execute_buy(signal, current_exposure)

        if not should_execute:
            logger.info(f"⏭️  SKIP {bucket}: {reason}")
            return

        # Validate token_id
        if not token_id:
            logger.error(f"❌ No token_id provided for {bucket}")
            return

        # Log signal details
        logger.info(f"\n{'='*60}")
        logger.info(f"💰 BUY Signal: Event {event_id} → {bucket}")
        logger.info(f"   Token ID: {token_id}")
        logger.info(f"   Model: {signal['model_prob']:.0%} vs Market: {signal['market_price']:.0%}")
        logger.info(f"   Edge: {signal['edge']:+.1%} | EV: ${signal['ev']:+.3f}/$")
        logger.info(f"   Kelly: {signal['kelly_fraction']:.1%} | Bet: ${signal['suggested_bet']:.2f}")
        logger.info(f"   Confidence: {signal['confidence']}")
        logger.info(f"{'='*60}\n")

        # Manual approval if required
        if self.config.require_approval:
            response = input("Execute this trade? (y/n): ")
            if response.lower() != 'y':
                logger.info("❌ Trade cancelled by user")
                return

        # Execute trade
        if self.config.dry_run:
            logger.info(f"🔧 DRY RUN: Would buy ${signal['suggested_bet']:.2f} of {bucket}")
        else:
            try:
                response = self.polymarket.place_market_buy(
                    token_id=token_id,
                    amount_usd=signal['suggested_bet']
                )

                logger.info(f"✅ Order executed: {response}")

            except Exception as e:
                logger.error(f"❌ Failed to execute trade: {e}")

    def check_stop_losses(self, positions: list):
        for position in positions:
            should_sell, reason = self.risk_manager.should_stop_loss(position)

            if should_sell:
                bucket = position.get("bucket")
                event_id = position.get("event_id")
                shares = position.get("tokens", 0)  # Note: API returns 'tokens' not 'shares'

                logger.warning(f"🚨 STOP-LOSS: {bucket} - {reason}")

                if self.config.dry_run:
                    logger.info(f"🔧 DRY RUN: Would sell {shares} shares of {bucket}")
                else:
                    try:
                        # Get current signals to find token_id
                        # (Portfolio endpoint doesn't include token_ids)
                        signals = self.polystrike.get_signals(self.config.bankroll)

                        # Find matching signal for this event/bucket
                        token_id = None
                        for event_signals in signals:
                            if event_signals.get("event_id") == event_id:
                                for sig in event_signals.get("signals", []):
                                    if sig.get("bucket") == bucket:
                                        token_id = sig.get("token_id")
                                        break
                            if token_id:
                                break

                        if not token_id:
                            logger.error(f"❌ Cannot sell {bucket}: token_id not found in current signals")
                            continue

                        # Execute market sell
                        response = self.polymarket.place_market_sell(
                            token_id=token_id,
                            shares=shares
                        )

                        logger.info(f"✅ Stop-loss executed: Sold {shares} shares of {bucket}")
                        logger.info(f"   Response: {response}")

                    except Exception as e:
                        logger.error(f"❌ Failed to execute stop-loss: {e}", exc_info=True)


def main():
    """Entry point."""
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()
