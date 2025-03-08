# simple_backtest.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz


# Generate test data directly
def generate_test_data(symbol, days=90):
    """Generate synthetic test data for backtesting"""
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=days)

    # Create date range (business days only)
    dates = pd.date_range(start=start_date, end=end_date, freq='B')

    # Set seed for reproducibility
    np.random.seed(42)

    # Generate price data
    base_price = 100.0
    daily_returns = np.random.normal(0.0005, 0.015, len(dates))
    cumulative_returns = np.cumprod(1 + daily_returns)
    closes = base_price * cumulative_returns

    # Generate OHLC
    volatility = 0.015
    opens = closes * np.exp(np.random.normal(-volatility / 2, volatility, len(dates)))
    highs = np.maximum(opens, closes) * np.exp(np.random.normal(volatility, volatility / 2, len(dates)))
    lows = np.minimum(opens, closes) * np.exp(np.random.normal(-volatility, volatility / 2, len(dates)))

    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': np.random.randint(1000, 10000, len(dates))
    })

    # Calculate RSI
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-10)  # Avoid division by zero
    df['rsi'] = 100 - (100 / (1 + rs))

    # Generate signals
    df['signal'] = 0
    df.loc[df['rsi'] < 30, 'signal'] = 1  # Buy
    df.loc[df['rsi'] > 70, 'signal'] = -1  # Sell

    return df


def run_simple_backtest(symbol):
    """Run a simple backtest using generated data"""
    # Generate test data
    print(f"Generating test data for {symbol}...")
    data = generate_test_data(symbol)

    # Run backtest
    initial_cash = 10000
    cash = initial_cash
    shares = 0
    portfolio_values = []
    trades = []

    for idx, row in data.iterrows():
        signal = row['signal']
        close_price = row['close']
        timestamp = row['timestamp']

        # Execute trades
        if signal == 1 and shares == 0:  # Buy
            shares_to_buy = int(cash / close_price)
            if shares_to_buy > 0:
                cost = shares_to_buy * close_price
                cash -= cost
                shares += shares_to_buy
                trades.append({
                    'date': timestamp,
                    'action': 'BUY',
                    'price': close_price,
                    'shares': shares_to_buy
                })
                print(f"BUY: {shares_to_buy} shares at ${close_price:.2f}")

        elif signal == -1 and shares > 0:  # Sell
            revenue = shares * close_price
            cash += revenue
            trades.append({
                'date': timestamp,
                'action': 'SELL',
                'price': close_price,
                'shares': shares
            })
            print(f"SELL: {shares} shares at ${close_price:.2f}")
            shares = 0

        # Track portfolio value
        portfolio_values.append({
            'date': timestamp,
            'total_value': cash + (shares * close_price),
            'cash': cash,
            'stock_value': shares * close_price,
            'close': close_price,
            'rsi': row['rsi']
        })

    # Convert to DataFrame
    portfolio_df = pd.DataFrame(portfolio_values)
    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

    # Calculate returns
    final_value = portfolio_df['total_value'].iloc[-1]
    total_return = ((final_value - initial_cash) / initial_cash) * 100

    # Print summary
    print(f"\nBacktest Summary for {symbol}:")
    print(f"Initial Cash: ${initial_cash:.2f}")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Number of Trades: {len(trades_df)}")

    # Plot results
    plot_results(symbol, portfolio_df, trades_df)

    return {
        'portfolio': portfolio_df,
        'trades': trades_df,
        'return': total_return
    }


def plot_results(symbol, portfolio, trades):
    """Plot backtest results"""
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]})

    # Plot portfolio value
    ax1.plot(portfolio['date'], portfolio['total_value'], label='Portfolio Value')
    ax1.set_title(f'Backtest Results for {symbol}')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.grid(True)

    # Plot stock price
    ax1_twin = ax1.twinx()
    ax1_twin.plot(portfolio['date'], portfolio['close'], 'r--', alpha=0.7, label='Stock Price')
    ax1_twin.set_ylabel('Stock Price ($)', color='r')

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Plot buy/sell points
    if not trades.empty:
        buy_trades = trades[trades['action'] == 'BUY']
        sell_trades = trades[trades['action'] == 'SELL']

        if not buy_trades.empty:
            ax1.scatter(buy_trades['date'], buy_trades['price'],
                        color='green', marker='^', s=100, label='Buy')

        if not sell_trades.empty:
            ax1.scatter(sell_trades['date'], sell_trades['price'],
                        color='red', marker='v', s=100, label='Sell')

    # Plot RSI
    ax2.plot(portfolio['date'], portfolio['rsi'], color='purple', label='RSI')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.3, label='Overbought')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.3, label='Oversold')
    ax2.set_ylabel('RSI')
    ax2.set_ylim([0, 100])
    ax2.grid(True)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Run a simple backtest for a single symbol
    symbol = "AAPL"
    results = run_simple_backtest(symbol)