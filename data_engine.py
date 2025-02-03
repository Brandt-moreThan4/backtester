import os
import time
import pandas as pd
import yfinance as yf
import constants as C
import streamlit as st

# DATA_FOLDER = 'data/'
DATA_FOLDER = 'temp_data/'
CACHE_EXPIRATION = 86400  # 1 day

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
        last_modified = os.path.getmtime(file_path)
        return (time.time() - last_modified) > CACHE_EXPIRATION

    def load_local_data(self, tickers: list[str]) -> pd.DataFrame:
        """Load data from local storage if available and not expired"""
        dfs = []
        for ticker in tickers:
            if self.is_cache_expired(ticker):
                # In theory, this should probably be checked on a per-ticker basis, but in practice it's probably fine...
                # print(f"Cache expired for {ticker}, refreshing data.")
                return None
            file_path = f'{DATA_FOLDER}{ticker}.csv'
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                # Reformat it back to how it comes from YF (multi-index)
                df.columns = pd.MultiIndex.from_product([[ticker], df.columns])

                dfs.append(df)
        return pd.concat(dfs, axis=1) if dfs else None

    def save_data_locally(self, df: pd.DataFrame, tickers: list[str]) -> None:
        """Save downloaded data locally to avoid frequent API calls"""
        os.makedirs(DATA_FOLDER, exist_ok=True)
        for ticker in tickers:
            # Drop the top column level to make it easier to work with
            # Drop nas to only save necessary rows fro this ticker
            mini_df = df[[ticker]].droplevel(0,axis=1).dropna()
            mini_df.to_csv(f'{DATA_FOLDER}{ticker}.csv')

    # @st.cache_data(ttl=86400)  # Cache at the Streamlit level for 24 hours
    def download_new_data(self, tickers: list[str]) -> pd.DataFrame:
        tickers = list(dict.fromkeys(tickers))  # Remove duplicates
        local_data = self.load_local_data(tickers)

        if local_data is not None and not local_data.isnull().all().all():
            print("Using cached data")
            self.raw_data_df = local_data
        else:
            print("Fetching new data from Yahoo Finance")
            self.raw_data_df = yf.download(tickers, group_by='ticker', auto_adjust=False,actions=False)
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


    #------ Load saved data
    # downloader.load_saved_data()

    #------ Downloading new Data

    # downloader.download_new_data(C.ALL_TICKERS)
    downloader.download_new_data(C.MARKET_TICKERS)

    # downloader.clean_data() 
    downloader.load_local_data(C.MARKET_TICKERS)

    # downloader.save_data()

    print('Done!')