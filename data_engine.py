import os
import time
import pandas as pd
import yfinance as yf
import datetime as dt
import constants as C
import streamlit as st

# DATA_FOLDER = 'data/'
DATA_FOLDER = 'temp_data/'
CACHE_EXPIRATION = 28800  # 8ish hours
MAX_FILES_SAVED = 100

class DataEngine:
    def __init__(self) -> None:
        self.adjusted_prices_df: pd.DataFrame = None
        self.rets_df: pd.DataFrame = None
        self.price_df: pd.DataFrame = None
        self.raw_data_df: pd.DataFrame = None

    def is_cache_expired(self, ticker: str) -> bool:
        file_path = f'{DATA_FOLDER}{ticker}.csv'
        if not os.path.exists(file_path):
            return True
        return (time.time() - os.path.getmtime(file_path)) > CACHE_EXPIRATION 

    def load_local_data(self, tickers: list[str]) -> pd.DataFrame:
        """Load data from local storage if available and not expired"""
        dfs = []
        for ticker in tickers:
            if self.is_cache_expired(ticker):
                return None
            file_path = f'{DATA_FOLDER}{ticker}.csv'
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                df.columns = pd.MultiIndex.from_product([[ticker], df.columns])
                dfs.append(df)
        return pd.concat(dfs, axis=1) if dfs else None

    def check_storage_limit(self):
        """Checks if adding new files will exceed MAX_FILES_SAVED and clears folder if necessary"""
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
            return
        
        existing_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
        if len(existing_files) >= MAX_FILES_SAVED:
            print("Storage limit exceeded, clearing folder...")
            for file in existing_files:
                os.remove(os.path.join(DATA_FOLDER, file))

    def save_data_locally(self, df: pd.DataFrame, tickers: list[str]) -> None:
        """Save downloaded data locally after checking storage limit"""
        self.check_storage_limit()
        os.makedirs(DATA_FOLDER, exist_ok=True)
        for ticker in tickers:
            mini_df = df[[ticker]].droplevel(0, axis=1).dropna()
            mini_df.to_csv(f'{DATA_FOLDER}{ticker}.csv')

    def download_new_data(self, tickers: list[str]) -> pd.DataFrame:
        tickers = list(dict.fromkeys(tickers))  # Remove duplicates
        local_data = self.load_local_data(tickers)

        if local_data is not None and not local_data.isnull().all().all():
            print("Using cached data")
            self.raw_data_df = local_data
        else:
            print("Fetching new data from Yahoo Finance")
            self.raw_data_df = yf.download(tickers, group_by='ticker', auto_adjust=False, actions=False)
            self.save_data_locally(self.raw_data_df, tickers)

        self.clean_data()
        return self.rets_df

    def clean_data(self) -> pd.DataFrame:
        df = self.raw_data_df.copy()
        df.index = pd.to_datetime(df.index)
        
        self.price_df = df.loc[:, (slice(None), 'Close')]
        self.price_df.columns = self.price_df.columns.droplevel(1)

        adjusted_prices_df = df.loc[:, (slice(None), 'Adj Close')].copy()
        adjusted_prices_df.columns = adjusted_prices_df.columns.droplevel(1)
        adjusted_prices_df.ffill(inplace=True)
        
        self.rets_df = adjusted_prices_df.pct_change(fill_method=None)
        self.rets_df = self.rets_df[sorted(self.rets_df.columns)].copy()
        self.adjusted_prices_df = adjusted_prices_df
        
        return self.rets_df

    def save_data(self, folder_path=DATA_FOLDER) -> None:
        os.makedirs(folder_path, exist_ok=True)
        self.rets_df.to_csv(f'{folder_path}rets_df.csv')
        self.adjusted_prices_df.to_csv(f'{folder_path}adjusted_prices_df.csv')
        self.price_df.to_csv(f'{folder_path}price_df.csv')

    @staticmethod
    def load_saved_data(folder: str = DATA_FOLDER) -> "DataEngine":
        dblob = DataEngine()
        dblob.rets_df = pd.read_csv(f'{folder}rets_df.csv', index_col=0, parse_dates=True)
        dblob.adjusted_prices_df = pd.read_csv(f'{folder}adjusted_prices_df.csv', index_col=0, parse_dates=True)
        dblob.price_df = pd.read_csv(f'{folder}price_df.csv', index_col=0, parse_dates=True)
        dblob.price_df.index = pd.to_datetime(dblob.price_df.index)
        return dblob
    
    @property
    def tickers(self) -> list[str]:
        return self.rets_df.columns.tolist()

if __name__ == '__main__':
    downloader = DataEngine()
    downloader.download_new_data(C.MARKET_TICKERS)
    downloader.load_local_data(C.MARKET_TICKERS)
    print('Done!')
