"""Client for Polystrike API."""
import requests
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class PolystrikeClient:
    """Client for consuming Polystrike prediction signals."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    def get_signals(self, bankroll: float) -> List[Dict]:
        """
        Fetch trading signals from Polystrike API.

        Args:
            bankroll: Your trading bankroll in USD

        Returns:
            List of signal dictionaries with BUY/HOLD/SKIP actions
        """
        try:
            url = f"{self.api_url}/signals/elon"
            params = {"bankroll": bankroll}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            signals = data.get("data", [])

            logger.info(f"Fetched {len(signals)} signals from Polystrike API")
            return signals

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch signals: {e}")
            return []

    def get_portfolio(self, wallet_address: str) -> Dict:
        """
        Fetch portfolio analysis for a wallet.

        Args:
            wallet_address: Ethereum wallet address

        Returns:
            Portfolio analysis with positions and recommendations
        """
        try:
            url = f"{self.api_url}/portfolio/elon"
            params = {"wallet": wallet_address}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get("data", [{}])[0]

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch portfolio: {e}")
            return {}
