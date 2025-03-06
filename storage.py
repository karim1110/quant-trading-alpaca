# data_storage.py
import sqlite3
import pandas as pd

class DataStorage:
    def __init__(self, db_name='market_data.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT,
            datetime TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            PRIMARY KEY (symbol, datetime)
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def store_data(self, symbol, df):
        """
        Stores market data for a symbol.
        Assumes the DataFrame's index is datetime and contains columns: open, high, low, close, volume.
        """
        if df.empty:
            return
        
        df = df.copy()
        df['symbol'] = symbol
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'datetime'}, inplace=True)
        try:
            df.to_sql('market_data', self.conn, if_exists='append', index=False)
        except Exception as e:
            print(f"Error storing data for {symbol}: {e}")
    
    def get_data(self, symbol):
        query = f"SELECT * FROM market_data WHERE symbol='{symbol}'"
        df = pd.read_sql(query, self.conn)
        return df
