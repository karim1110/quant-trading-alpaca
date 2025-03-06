# alpaca_api.py
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class AlpacaAPI:
    def __init__(self, api_key, api_secret, paper=True):
        # Instantiate the TradingClient for order management and account info
        self.client = TradingClient(api_key, api_secret, paper=paper)
    
    def get_account_info(self):
        account = self.client.get_account()
        return account

    def get_buying_power(self):
        account = self.get_account_info()
        return account.buying_power

    def get_position(self, symbol):
        try:
            position = self.client.get_open_position(symbol)
            return position
        except Exception as e:
            # If no position exists, return None
            # print(f"Position for {symbol} not found: {e}")
            return None

    def list_positions(self):
        positions = self.client.get_all_positions()
        return positions
    
    def submit_market_order(self, symbol, qty, side, time_in_force=TimeInForce.DAY):
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force
        )
        order = self.client.submit_order(order_data=order_data)
        return order
    
    def submit_limit_order(self, symbol, qty, side, limit_price, time_in_force=TimeInForce.DAY):
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force,
            limit_price=limit_price
        )
        order = self.client.submit_order(order_data=order_data)
        return order

    def cancel_all_orders(self):
        orders = self.client.get_orders()
        for order in orders:
            self.client.cancel_order(order.id)
