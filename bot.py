"""Main trading bot loop."""
import logging
import time
import sys
from datetime import datetime

from config import load_config
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

        # Risk check
        should_execute, reason = self.risk_manager.should_execute_buy(signal, current_exposure)

        if not should_execute:
            logger.info(f"⏭️  SKIP {bucket}: {reason}")
            return

        # Log signal details
        logger.info(f"\n{'='*60}")
        logger.info(f"💰 BUY Signal: Event {event_id} → {bucket}")
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
                # TODO: Need to map bucket to token_id
                # This requires additional API endpoint or market discovery
                token_id = self.get_token_id_for_bucket(event_id, bucket)

                if not token_id:
                    logger.error(f"❌ Could not find token_id for {bucket}")
                    return

                response = self.polymarket.place_market_buy(
                    token_id=token_id,
                    amount_usd=signal['suggested_bet']
                )

                logger.info(f"✅ Order executed: {response}")

            except Exception as e:
                logger.error(f"❌ Failed to execute trade: {e}")

    def check_stop_losses(self, positions: list):
        """Check all positions for stop-loss triggers."""
        for position in positions:
            should_sell, reason = self.risk_manager.should_stop_loss(position)

            if should_sell:
                bucket = position.get("bucket")
                logger.warning(f"🚨 STOP-LOSS: {bucket} - {reason}")

                if self.config.dry_run:
                    logger.info(f"🔧 DRY RUN: Would sell {bucket}")
                else:
                    try:
                        # TODO: Execute sell order
                        logger.info(f"Selling {bucket}...")
                    except Exception as e:
                        logger.error(f"❌ Failed to execute stop-loss: {e}")

    def get_token_id_for_bucket(self, event_id: int, bucket: str) -> str | None:
        """
        Map event_id + bucket to Polymarket token_id.

        TODO: This needs to be implemented by either:
        1. Adding a /markets endpoint to Polystrike API
        2. Using Polymarket's market discovery API
        3. Maintaining a local cache of event_id -> token_id mappings
        """
        # Placeholder - needs implementation
        logger.warning("Token ID mapping not implemented yet")
        return None


def main():
    """Entry point."""
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()
