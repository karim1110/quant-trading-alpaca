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
startup_period_minutes = 30  # Accumulate data for 30 minutes before trading

def accumulate_data():
    """Collect market data for all assets for a set period so we have enough history for our strategy."""
    print(f"Accumulating data for {startup_period_minutes} minutes for assets: {assets}")
    start_time = datetime.datetime.utcnow()
    while (datetime.datetime.utcnow() - start_time).total_seconds() < startup_period_minutes * 60:
        now = datetime.datetime.utcnow().replace(microsecond=0)
        current_time = now.isoformat() + "Z"
        for symbol in assets:
            latest_price = data_api.get_latest_price(symbol, timeframe=timeframe)
            if latest_price is not None:
                print(f"{current_time} - Latest price for {symbol}: {latest_price}")
                # Create a dummy OHLCV row. In production, store complete OHLCV data.
                dummy_data = pd.DataFrame({
                    'open': [latest_price],
                    'high': [latest_price],
                    'low': [latest_price],
                    'close': [latest_price],
                    'volume': [0]
                }, index=[current_time])
                storage.store_data(symbol, dummy_data)
            else:
                print(f"No data retrieved for {symbol} this cycle.")
        time.sleep(order_interval)
    print("Data accumulation complete.")

def run_trading_loop():
    """After accumulating data, run the trading loop over each asset."""
    print("Starting trading loop. Press Ctrl+C to exit.")
    try:
        while True:
            now = datetime.datetime.utcnow().replace(microsecond=0)
            current_time = now.isoformat() + "Z"
            for symbol in assets:
                latest_price = data_api.get_latest_price(symbol, timeframe=timeframe)
                print(f"{current_time} - Latest price for {symbol}: {latest_price}")
                
                # Retrieve historical data for the asset from SQLite
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
    # Phase 1: Accumulate market data for each asset
    accumulate_data()
    # Phase 2: Start trading using the accumulated data
    run_trading_loop()
