# strategy.py
import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def simple_rsi_strategy(data, rsi_overbought=70, rsi_oversold=30):
    """
    Implements a simple RSI strategy.
    - If RSI is below the oversold threshold, return 'buy'.
    - If RSI is above the overbought threshold, return 'sell'.
    - Otherwise, return 'hold'.
    
    Expects `data` to be a DataFrame with at least a 'close' column.
    """
    if data.empty or len(data) < 15:
        return 'hold'
    
    data = data.copy()
    data['rsi'] = calculate_rsi(data['close'])
    latest_rsi = data['rsi'].iloc[-1]
    
    if latest_rsi < rsi_oversold:
        return 'buy'
    elif latest_rsi > rsi_overbought:
        return 'sell'
    else:
        return 'hold'
