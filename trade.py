# main.py
import time
import datetime
import pandas as pd
from api import AlpacaAPI
from data import AlpacaData
from strategy import simple_rsi_strategy
from storage import DataStorage
from alpaca.trading.enums import OrderSide

# --- Credentials ---
API_KEY = 'PK0JVFL1YNYX41NG3RDN'
API_SECRET = 'UzXIxDYf0olPlcmseJfbrvJeR73GQQ98IhWquDqN'

# --- Instantiate Modules ---
trading_api = AlpacaAPI(API_KEY, API_SECRET, paper=True)
data_api = AlpacaData(API_KEY, API_SECRET, base_url='https://paper-api.alpaca.markets', api_version='v2')
storage = DataStorage()

# --- Define the list of assets ---
assets = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']  

timeframe = '1Min'
order_interval = 60  # seconds between iterations

def fetch_initial_data():
    """
    Immediately fetch historical data for each asset over a defined period (e.g., last 60 minutes)
    so that your strategy has data to work with right away.
    """
    print("Fetching historical data for assets:", assets)
    end_time = datetime.datetime.utcnow().replace(microsecond=0)
    # For example, fetch the last 60 minutes of data
    start_time = end_time - datetime.timedelta(minutes=60)
    start_iso = start_time.isoformat() + "Z"
    end_iso = end_time.isoformat() + "Z"
    
    for symbol in assets:
        df = data_api.get_historical_data(symbol, timeframe, start_iso, end_iso)
        if not df.empty:
            print(f"{symbol}: Fetched data from {start_iso} to {end_iso}")
            storage.store_data(symbol, df)
        else:
            print(f"{symbol}: No historical data fetched.")
    print("Historical data fetch complete.")

def run_trading_loop():
    """After fetching initial data, run the trading loop over each asset."""
    print("Starting trading loop. Press Ctrl+C to exit.")
    try:
        while True:
            now = datetime.datetime.utcnow().replace(microsecond=0)
            current_time = now.isoformat() + "Z"
            # Retrieve latest prices for all assets using get_latest_bars (or individually)
            latest_prices = data_api.get_latest_prices(assets, feed='iex')
            
            for symbol in assets:
                latest_price = latest_prices.get(symbol, None)
                print(f"{current_time} - Latest price for {symbol}: {latest_price}")
                
                # Create a dummy OHLCV row for the latest price
                if latest_price is not None:
                    new_data = pd.DataFrame({
                        'open': [latest_price],
                        'high': [latest_price],
                        'low': [latest_price],
                        'close': [latest_price],
                        'volume': [0],
                        'trade_count': [0],
                        'vwap': [latest_price]
                    }, index=[current_time])
                    storage.store_data(symbol, new_data)
                
                # Retrieve updated historical data from SQLite
                historical_data = storage.get_data(symbol)
                if historical_data.empty:
                    print(f"Historical data not available for {symbol}. Skipping strategy evaluation.")
                    signal = 'hold'
                else:
                    signal = simple_rsi_strategy(historical_data)
                print(f"Strategy signal for {symbol}: {signal}")
                
                # Check current position for the asset
                position = trading_api.get_position(symbol)
                
                # Trading logic: Buy if signal is 'buy' and no position; sell if signal is 'sell' and holding a position.
                if signal == 'buy' and position is None:
                    print(f"Placing buy order for {symbol}...")
                    trading_api.submit_market_order(symbol, qty=1, side=OrderSide.BUY)
                elif signal == 'sell' and position is not None:
                    print(f"Placing sell order for {symbol}...")
                    trading_api.submit_market_order(symbol, qty=1, side=OrderSide.SELL)
                else:
                    print(f"No action taken for {symbol}.")
            time.sleep(order_interval)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Cancelling any open orders and exiting...")
        trading_api.cancel_all_orders()
        print("Done.")

if __name__ == '__main__':
    # Phase 1: Immediately fetch historical data for each asset
    fetch_initial_data()
    # Phase 2: Start trading using the fetched historical data
    run_trading_loop()
