# alpaca_data.py
import alpaca_trade_api as tradeapi
import pandas as pd

class AlpacaData:
    def __init__(self, api_key, api_secret, base_url='https://paper-api.alpaca.markets', api_version='v2'):
        # Use the REST client from alpaca_trade_api for market data.
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version=api_version)
    
    def get_latest_price(self, symbol, timeframe='1Min', limit=1, feed='iex'):
        # We can keep this function for single-symbol queries if needed
        try:
            bars = self.api.get_bars(symbol, timeframe, limit=limit, feed=feed)
            df = bars.df
            return df['close'].iloc[-1]
        except Exception as e:
            print(f"Error retrieving latest price for {symbol}: {e}")
            return None
    
    def get_latest_prices(self, symbols, feed='iex'):
        """
        Retrieves the latest bar for each symbol in the provided list using get_latest_bars.
        Returns a dictionary mapping each symbol to its latest close price.
        """
        try:
            latest_bars = self.api.get_latest_bars(symbols, feed=feed)
            # latest_bars is a dictionary mapping symbol -> Bar object.
            prices = {symbol: latest_bars[symbol].c for symbol in symbols if symbol in latest_bars}
            return prices
        except Exception as e:
            print(f"Error retrieving latest prices for {symbols}: {e}")
            return {}
    
    def get_historical_data(self, symbol, timeframe, start, end, feed='iex'):
        try:
            bars = self.api.get_bars(symbol, timeframe, start=start, end=end, feed=feed)
            df = bars.df
            return df
        except Exception as e:
            print(f"Error retrieving historical data for {symbol}: {e}")
            return pd.DataFrame()
