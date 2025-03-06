# alpaca_data.py
import alpaca_trade_api as tradeapi
import pandas as pd

class AlpacaData:
    def __init__(self, api_key, api_secret, base_url='https://paper-api.alpaca.markets', api_version='v2'):
        # Use the REST client from alpaca_trade_api for market data.
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version=api_version)
    
    def get_latest_price(self, symbol, timeframe='1Min', limit=1):
        try:
            bars = self.api.get_bars(symbol, timeframe, limit=limit)
            df = bars.df
            return df['close'].iloc[-1]
        except Exception as e:
            print(f"Error retrieving latest price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, timeframe, start, end):
        try:
            bars = self.api.get_bars(symbol, timeframe, start=start, end=end)
            df = bars.df
            return df
        except Exception as e:
            print(f"Error retrieving historical data for {symbol}: {e}")
            return pd.DataFrame()
