import logging
from bot.client import BinanceFuturesClient

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        params = {'symbol': symbol, 'side': side.upper(), 'type': 'MARKET', 'quantity': quantity}
        return self.client.execute_order(**params)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        params = {'symbol': symbol, 'side': side.upper(), 'type': 'LIMIT', 'timeInForce': 'GTC', 'quantity': quantity, 'price': price}
        return self.client.execute_order(**params)
        
    def place_stop_market_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        params = {'symbol': symbol, 'side': side.upper(), 'type': 'STOP_MARKET', 'quantity': quantity, 'stopPrice': stop_price}
        return self.client.execute_order(**params)

    def modify_limit_order(self, symbol: str, side: str, quantity: float, price: float, order_id: int) -> dict:
        params = {'symbol': symbol, 'side': side.upper(), 'quantity': quantity, 'price': price, 'orderId': order_id}
        return self.client.modify_order(**params)
        
    def cancel_specific_order(self, symbol: str, order_id: int) -> dict:
        return self.client.cancel_order(symbol, order_id)

    def place_grid_basket_order(self, symbol: str, side: str, total_quantity: float, start_price: float, levels: int, price_step: float) -> list:
        """Places a basket of scaling Limit orders (Bonus Feature)."""
        logger.info(f"Placing Grid/Basket Order: {levels} levels for {symbol}")
        qty_per_level = round(total_quantity / levels, 3)
        responses = []
        
        for i in range(levels):
            # Drops the price for BUY limits, raises the price for SELL limits
            current_price = start_price - (i * price_step) if side.upper() == 'BUY' else start_price + (i * price_step)
            params = {
                'symbol': symbol,
                'side': side.upper(),
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': qty_per_level,
                'price': round(current_price, 2)
            }
            try:
                responses.append(self.client.execute_order(**params))
            except Exception as e:
                logger.error(f"Grid level {i} failed: {e}")
                
        return responses