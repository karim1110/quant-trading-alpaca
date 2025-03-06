# data_storage.py
import sqlite3
import pandas as pd

class DataStorage:
    def __init__(self, db_name='market_data.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.create_table()

    def create_table(self):
        # Updated schema to include trade_count and vwap.
        query = """
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT,
            timestamp TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            trade_count INTEGER,
            vwap REAL,
            PRIMARY KEY (symbol, timestamp)
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def store_data(self, symbol, df):
        """
        Stores market data for a symbol.
        Expects the DataFrame to have an index or column that will be renamed to 'timestamp'
        and columns: o, h, l, c, v, n, vw.
        """
        if df.empty:
            return
        
        df = df.copy()
        df['symbol'] = symbol
        df.reset_index(inplace=True)
        # Rename index column or column 't' to 'timestamp'
        if 'index' in df.columns:
            df.rename(columns={'index': 'timestamp'}, inplace=True)
        if 't' in df.columns:
            df.rename(columns={'t': 'timestamp'}, inplace=True)
        
        # Map API columns to our table columns.
        mapping = {
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            'n': 'trade_count',
            'vw': 'vwap'
        }
        df.rename(columns=mapping, inplace=True)
        
        # Optional: drop any columns not defined in our table.
        desired_columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
        df = df[desired_columns]
        
        try:
            df.to_sql('market_data', self.conn, if_exists='append', index=False)
        except Exception as e:
            print(f"Error storing data for {symbol}: {e}")
    
    def get_data(self, symbol):
        query = f"SELECT * FROM market_data WHERE symbol='{symbol}'"
        df = pd.read_sql(query, self.conn)
        return df
