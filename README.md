# quant-trading-alpaca

## Introduction
This trading system aims to implement a simple yet effective algorithmic trading strategy using the Alpaca API to automate financial asset trading. The system retrieves market data, processes it to generate signals based on technical indicators, and then executes trades according to predefined strategies. By leveraging technical analysis such as the Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD), and Bollinger Bands, the system evaluates market conditions and determines when to buy or sell assets. Additionally, the system integrates with Alpaca’s paper trading feature for risk-free simulation of live market conditions, allowing for real-time performance monitoring and refinement of the trading strategy.

The main goals of the system are:

Automating market data retrieval and trading decisions.
Implementing a multi-factor trading strategy based on technical indicators.
Optimizing risk management strategies and tracking portfolio performance.
Utilizing Alpaca's paper trading to simulate trades and evaluate the effectiveness of the strategy in real-time conditions.

## Market Data Retrieval
The Alpaca trading system retrieves market data through the alpaca-py library, which allows seamless access to both real-time and historical market data via Alpaca’s REST API. The data is fetched for multiple assets, and the system utilizes this data to generate trading signals based on predefined strategies.

Code Snippets:
Alpaca API Client (api.py): The AlpacaAPI class encapsulates the Alpaca API client for order management and retrieving market data.

get_account_info(): Retrieves account information, including available buying power.
get_position(symbol): Retrieves the current position of a specific asset in the portfolio.
submit_market_order() and submit_limit_order(): Submits market and limit orders for trading the assets.
Data Retrieval Class (data.py): The AlpacaData class interacts directly with the Alpaca API to fetch market data.

get_latest_price(): Retrieves the most recent closing price for a single asset.
get_latest_prices(): Retrieves the latest closing prices for multiple assets in a batch request.
get_historical_data(): Fetches historical market data for a given asset within a specific time range.

class AlpacaData:
    def __init__(self, api_key, api_secret, base_url='https://paper-api.alpaca.markets', api_version='v2'):
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version=api_version)

    def get_latest_price(self, symbol, timeframe='1Min', limit=1, feed='iex'):
        try:
            bars = self.api.get_bars(symbol, timeframe, limit=limit, feed=feed)
            df = bars.df
            return df['close'].iloc[-1]
        except Exception as e:
            print(f"Error retrieving latest price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, timeframe, start, end, feed='iex'):
        try:
            bars = self.api.get_bars(symbol, timeframe, start=start, end=end, feed=feed)
            df = bars.df
            return df
        except Exception as e:
            print(f"Error retrieving historical data for {symbol}: {e}")
            return pd.DataFrame()

def fetch_initial_data():
    print("Fetching historical data for assets:", assets)
    end_time = datetime.datetime.utcnow().replace(microsecond=0)
    start_time = end_time - datetime.timedelta(minutes=60)
    start_iso = start_time.isoformat() + "Z"
    end_iso = end_time.isoformat() + "Z"
    
    for symbol in assets:
        df = data_api.get_historical_data(symbol, timeframe, start_iso, end_iso)
        if not df.empty:
            storage.store_data(symbol, df)
        else:
            print(f"{symbol}: No historical data fetched.")

Trading Loop (trade.py): The trading loop retrieves the latest prices and historical data for multiple assets, stores the data, and then evaluates it using the trading strategy. For each asset:

The most recent market data is fetched using the get_latest_prices() method.
A trading signal is generated based on the historical data and the selected strategy.
If the signal is to buy or sell, the corresponding market order is executed.

def run_trading_loop():
    print("Starting trading loop. Press Ctrl+C to exit.")
    try:
        while True:
            latest_prices = data_api.get_latest_prices(assets, feed='iex')
            for symbol in assets:
                latest_price = latest_prices.get(symbol, None)
                if latest_price is not None:
                    new_data = pd.DataFrame({
                        'open': [latest_price],
                        'high': [latest_price],
                        'low': [latest_price],
                        'close': [latest_price],
                        'volume': [0],
                    }, index=[current_time])
                    storage.store_data(symbol, new_data)

            historical_data = storage.get_data(symbol)
            if not historical_data.empty:
                signal = simple_rsi_strategy(historical_data)
            else:
                signal = 'hold'

            if signal == 'buy' and position is None:
                trading_api.submit_market_order(symbol, qty=1, side=OrderSide.BUY)
            elif signal == 'sell' and position is not None:
                trading_api.submit_market_order(symbol, qty=1, side=OrderSide.SELL)

## Data Storage Strategy:
The trading system stores market data using an SQLite database for efficient management and easy access. Each asset’s data (OHLCV) is stored in a separate table, with timestamps recorded in UTC to avoid time zone discrepancies. The data is stored in minute-level timeframes (e.g., 1Min), ensuring precise tracking of market movements.

Key Points:
Storage Method: SQLite database for structured data storage and CSV files for backups.
Data Structure: Each asset has its own table with columns for timestamp, open, high, low, close, volume, and VWAP.
Timestamps: All timestamps are in UTC format to maintain consistency across assets and time zones.
Data Insertion: New data is added after every trading loop iteration, ensuring real-time updates.

def store_data(self, symbol, data):
    # Store OHLCV data in SQLite database
    cursor.execute(f'INSERT OR REPLACE INTO {symbol} (timestamp, open, high, low, close, volume, vwap) VALUES (?, ?, ?, ?, ?, ?, ?)', (row.name, row['open'], row['high'], row['low'], row['close'], row['volume'], row['vwap']))

## Trading Strategy Development:
The development of the trading strategy involves the following steps:

1. Baseline Model:
The initial trading strategy used the Relative Strength Index (RSI) as the primary indicator to generate buy and sell signals. This baseline model helps in identifying overbought or oversold conditions in the market, which are used as entry and exit points for trades.

RSI Calculation: The RSI was calculated using a 14-period window. If the RSI was below 30 (oversold), the strategy would signal a "buy" trade. If the RSI was above 70 (overbought), it would signal a "sell" trade. Otherwise, the system would hold.

Backtest Results: The backtest for AAPL with this strategy showed an initial investment of $10,000, which grew to $10,141.96, yielding a total return of 1.42% over 20 trades.

def simple_rsi_strategy(data, rsi_overbought=70, rsi_oversold=30):
    """RSI-based strategy: Buy when RSI is below 30, sell when RSI is above 70"""
    data['rsi'] = calculate_rsi(data['close'])
    latest_rsi = data['rsi'].iloc[-1]
    if latest_rsi < rsi_oversold:
        return 'buy'
    elif latest_rsi > rsi_overbought:
        return 'sell'
    else:
        return 'hold'


2. Advanced Models:
Two advanced models were developed by incorporating multiple technical indicators to improve the strategy's performance. These models included the following indicators:

RSI: Retained from the baseline model to track overbought and oversold conditions.
Momentum: Calculated as the percentage change over a specified period, helping to identify the strength of a trend.
MACD: The Moving Average Convergence Divergence was used to identify trend reversals by comparing short-term and long-term moving averages.
Bollinger Bands: Used to gauge volatility and potential price levels at which to buy or sell.
ADX (Average Directional Index): Helps to identify trend strength, informing the model whether a trend is strong enough to justify taking a position.
ATR (Average True Range): Measures market volatility and is used for setting stop-loss or take-profit levels.

These indicators were combined using a multi-factor strategy, where each signal (buy, sell, hold) was weighted, and a combined score was calculated to generate the final trading decision.

3. Risk Management:
Risk management is incorporated into the strategy using indicators like ADX and ATR, which help determine the strength of trends and market volatility. For example:

The ADX threshold was set to 25 to ensure trades are taken only during strong trends.
Position Sizing: Based on volatility (ATR), position sizes were adjusted dynamically to manage risk and prevent overexposure in highly volatile conditions.
4. Position Sizing:
The position size was dynamically adjusted based on market volatility using the ATR. Larger positions were taken when volatility was low, and smaller positions were taken when volatility increased, to manage risk.

5. Backtest Results:
The backtest results showed a total return of -3.24% for AAPL over 18 trades with the advanced strategy. The negative result suggested that while the strategy is robust in terms of risk management, it may need further optimization or tweaking of indicator thresholds to improve its performance.

### Multi-factor strategy that combines RSI, Momentum, MACD, Bollinger Bands, ADX, and ATR: 
def multi_factor_strategy(data, config=None):
    # Combine the signals from multiple indicators to generate a final signal
    if score > config['buy_threshold']:
        return 'buy'
    elif score < config['sell_threshold']:
        return 'sell'
    else:
        return 'hold'
        
The baseline RSI strategy performed better in terms of returns but the multi-factor strategy provided stronger risk management. Further optimizations will be needed for the advanced models to improve profitability.

## Automation and Scheduling:
The data retrieval process for the trading system is fully automated, ensuring continuous updates to market data and the execution of trading strategies without manual intervention. Here's how the automation is implemented:

1. Automated Data Retrieval:
The market data retrieval is automated using the Alpaca API, which fetches the latest market data at regular intervals. The system retrieves both historical data for backtesting and real-time data for live trading.

Historical Data Fetching: The system initially fetches a set of historical data for each asset when it starts up. This is done by calling the get_historical_data method of the AlpacaData class.
Real-Time Data Fetching: Once the initial data is retrieved, the system enters a loop, continuously fetching the latest prices every minute (or a predefined timeframe) using the get_latest_prices method.

def fetch_initial_data():
    """Fetch historical data for each asset over a defined period."""
    for symbol in assets:
        df = data_api.get_historical_data(symbol, timeframe, start_iso, end_iso)
        if not df.empty:
            storage.store_data(symbol, df)

def run_trading_loop():
    """Continuously fetch latest prices and execute trades."""
    while True:
        latest_prices = data_api.get_latest_prices(assets, feed='iex')
        for symbol in assets:
            # Process and store data
            latest_price = latest_prices.get(symbol, None)
            if latest_price is not None:
                # Store the latest market data in the database
                storage.store_data(symbol, new_data)

2. Task Scheduling:
The data retrieval and trading loop are scheduled to run periodically. The trading loop runs continuously in the background, with each iteration fetching the latest data and making trading decisions based on the defined strategy.

The loop executes every minute, ensuring that the strategy is updated and trades are placed in real-time. This is accomplished by using time.sleep() to pause the loop between iterations.

order_interval = 60  # seconds between iterations
time.sleep(order_interval)

This ensures that the trading system continuously retrieves and updates market data while minimizing resource consumption when the market is idle.

3. Error Handling:
To ensure the robustness of the system, error handling mechanisms are integrated throughout the data retrieval and trading execution processes:

API Errors: If an error occurs while fetching data from the Alpaca API (e.g., network issues or data not available), the system handles the exception and logs the error without crashing.

try:
    latest_prices = data_api.get_latest_prices(assets, feed='iex')
except Exception as e:
    print(f"Error retrieving latest prices for {assets}: {e}")

Trading Errors: If there is an issue with placing orders (e.g., invalid positions or failed trades), the system logs the error and attempts to retry after a delay.

try:
    trading_api.submit_market_order(symbol, qty=1, side=OrderSide.BUY)
except Exception as e:
    print(f"Error placing buy order for {symbol}: {e}")

Logging: All actions (e.g., fetching data, placing orders, errors) are logged for debugging and performance monitoring. The system logs key events, such as when new data is fetched or when an order is placed, to ensure traceability of the trading operations.

def log_action(message):
    with open('trade_log.txt', 'a') as log_file:
        log_file.write(f"{datetime.datetime.now()} - {message}\n")

4. Script Version Control:
The system is version-controlled using Git, allowing for effective collaboration and easy tracking of changes in the trading logic and data retrieval process.

Version Control: The entire trading system is maintained in a Git repository, where changes to the strategy, data retrieval methods, or other parts of the code are tracked. This makes it easy to roll back to previous versions of the code or make collaborative changes.

git init  # Initialize the git repository
git add .  # Add files to the staging area
git commit -m "Initial commit with automated data retrieval"
git push origin main  # Push changes to remote repository

Branching: New features, bug fixes, or changes to the strategy can be developed in separate branches, which are then merged back into the main branch after review.

git checkout -b new_feature
git merge new_feature  # Merge feature branch back into main

5. Monitoring and Alerts:
The system includes basic monitoring features where key performance metrics, such as profit and loss, number of trades, and portfolio value, are logged and reviewed periodically. Alerts can be set up (e.g., using email or SMS) if specific thresholds are crossed, such as large drawdowns or failed trades.

Performance Monitoring: Metrics are logged during backtesting and live trading to assess the system's performance over time.
Alerts: If the system encounters unexpected conditions or performance issues, alerts are generated, and the team can act promptly.

Conclusion:
Through automation, error handling, and logging, the trading system operates continuously, retrieving and updating market data, making real-time trading decisions, and ensuring that operations are efficient and reliable. The use of version control further ensures that any updates to the system are tracked, enabling easy management and collaboration.

## Paper Trading and Monitoring:
The system uses Alpaca's paper trading feature to simulate live market conditions without real financial risk. Paper trading allows the algorithm to execute buy and sell orders based on real-time market data, but without impacting actual capital. The performance of the algorithm is monitored by tracking key metrics such as portfolio value, trade outcomes, and overall returns, providing valuable insights into its effectiveness in a risk-free environment.

## Results and Lessons Learned:
The baseline RSI strategy yielded a small positive return of 1.42%, while the multi-factor strategy performed with a -3.24% return. This suggests that while the multi-factor strategy enhanced risk management, it may need further optimization to improve profitability. Key challenges included fine-tuning indicator thresholds and managing market volatility. Lessons learned include the importance of adjusting risk management parameters and improving signal accuracy. Future iterations will focus on further strategy refinement and optimizing performance in volatile market conditions.

## Compliance and Legal Considerations:
Algorithmic trading must comply with relevant financial regulations, such as FINRA and SEC guidelines in the U.S. The system ensures that trades are executed within the constraints of Alpaca's paper trading environment, which simulates real market conditions without violating regulatory rules. Compliance with market conduct standards, such as ensuring no market manipulation or insider trading, is a priority.

## Conclusion:
This project successfully developed and tested an algorithmic trading system using Alpaca's API. The system retrieved real-time and historical market data, applied trading strategies, and performed paper trading. Despite some challenges with strategy performance, the project provided valuable insights into algorithmic trading, offering a foundation for further development and optimization. Key achievements include automating the trading process, utilizing risk management techniques, and simulating live trading conditions in a risk-free environment.



