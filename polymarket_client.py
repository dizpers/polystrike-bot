"""Wrapper for Polymarket py-clob-client."""
import logging
from typing import Dict
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

logger = logging.getLogger(__name__)


class PolymarketClient:
    """Simplified wrapper for Polymarket CLOB client."""

    def __init__(self, private_key: str, chain_id: int = 137):
        """
        Initialize Polymarket client.

        Args:
            private_key: Wallet private key (with 0x prefix)
            chain_id: Chain ID (137 for Polygon mainnet)
        """
        self.client = ClobClient(
            key=private_key,
            chain_id=chain_id,
            signature_type=0  # EOA wallet (MetaMask)
        )
        self.client.set_api_creds(self.client.create_or_derive_api_creds())
        logger.info("Polymarket client initialized")

    def place_market_buy(self, token_id: str, amount_usd: float) -> Dict:
        """
        Place a market buy order.

        Args:
            token_id: Polymarket token ID for the outcome
            amount_usd: Dollar amount to spend

        Returns:
            Order response dictionary
        """
        try:
            order = MarketOrderArgs(
                token_id=token_id,
                amount=amount_usd,
                side=BUY,
                order_type=OrderType.FOK  # Fill or Kill
            )

            signed_order = self.client.create_market_order(order)
            response = self.client.post_order(signed_order, OrderType.FOK)

            logger.info(f"Market BUY: {amount_usd} USD on token {token_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to place market buy: {e}")
            raise

    def place_market_sell(self, token_id: str, shares: float) -> Dict:
        """
        Place a market sell order.

        Args:
            token_id: Polymarket token ID
            shares: Number of shares to sell

        Returns:
            Order response dictionary
        """
        try:
            # For selling, we use limit order at very low price to ensure fill
            order = OrderArgs(
                token_id=token_id,
                price=0.01,  # Sell at any price
                size=shares,
                side=SELL
            )

            signed_order = self.client.create_order(order)
            response = self.client.post_order(signed_order, OrderType.GTC)

            logger.info(f"Market SELL: {shares} shares of token {token_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to place market sell: {e}")
            raise

    def get_balance(self) -> float:
        """
        Get USDC balance for the wallet.

        Returns:
            USDC balance as float
        """
        try:
            # py-clob-client provides get_balance() method
            balance = self.client.get_balance()
            logger.info(f"USDC Balance: ${balance:.2f}")
            return float(balance)
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0
