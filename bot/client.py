import os
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """A robust wrapper for the Binance Futures Testnet client."""
    def __init__(self):
        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

        if not self.api_key or not self.api_secret:
            logger.error("Missing credentials.")
            raise ValueError("Binance API keys must be set in environment variables.")

        try:
            self._client = Client(self.api_key, self.api_secret, testnet=True)
            self._client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            self._client.futures_ping()
            logger.info("Successfully connected to Binance Futures Testnet (USDT-M).")
        except Exception as e:
            logger.critical(f"Unexpected error during client setup: {str(e)}")
            raise

    def execute_order(self, **kwargs) -> dict:
        try:
            response = self._client.futures_create_order(**kwargs)
            logger.info(f"Order executed successfully. ID: {response.get('orderId')}")
            return response
        except Exception as e:
            logger.error(f"API Error placing order: {str(e)}")
            raise

    def modify_order(self, **kwargs) -> dict:
        try:
            response = self._client.futures_modify_order(**kwargs)
            logger.info(f"Order modified successfully. ID: {response.get('orderId')}")
            return response
        except Exception as e:
            logger.error(f"API Error modifying order: {str(e)}")
            raise

    def get_open_orders(self, symbol: str) -> list:
        """Fetches all active open orders from the exchange for a specific symbol."""
        try:
            return self._client.futures_get_open_orders(symbol=symbol)
        except Exception as e:
            logger.error(f"Error fetching open orders: {str(e)}")
            raise
            
    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancels a specific active order on the exchange."""
        try:
            response = self._client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order {order_id} cancelled successfully.")
            return response
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            raise