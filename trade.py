
import alpaca_trade_api as tradeapi
import time
#import quickfix as fix
#import quickfix42 as fix42

# Set your Alpaca API key and secret
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
BASE_URL = 'https://paper-api.alpaca.markets'  # Use paper trading base URL for testing

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

# Specify the asset symbol and trading interval
symbol = 'AAPL'  # Replace with your desired stock symbol
interval = 5  # Time interval in seconds

# Main trading loop
while True:
    try:
        # Get historical market data for the specified symbol and interval
        historical_data = api.get_barset(symbol, '1Min', limit=1).df[symbol]

        # Get the last close price
        last_close_price = historical_data['close'].iloc[-1]

        # Determine whether to place a Buy or Sell order based on alternating intervals
        if time.time() % (2 * interval) < interval:
            # Place Buy order
            api.submit_order(
                symbol=symbol,
                qty=1,  # Adjust quantity as needed
                side='buy',
                type='limit',
                time_in_force='gtc',
                limit_price=last_close_price * 1.01,  # Place a limit order slightly above the current price
            )
            print("Buy order placed at {}".format(last_close_price))

        else:
            # Place Sell order
            api.submit_order(
                symbol=symbol,
                qty=1,  # Adjust quantity as needed
                side='sell',
                type='limit',
                time_in_force='gtc',
                limit_price=last_close_price * 0.99,  # Place a limit order slightly below the current price
            )
            print("Sell order placed at {}".format(last_close_price))

        # Wait for the next interval
        time.sleep(interval)

    except Exception as e:
        print(f"An error occurred: {e}")
        # Add proper error handling based on your requirements
