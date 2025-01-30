import pandas as pd
import yfinance as yf
DATA_FOLDER = 'data/'



class DataBlob:

    def __init__(self,tickers:list[str],download:bool=True) -> None:
        self.input_tickers = tickers
        self.adjusted_prices_df:pd.DataFrame = None
        self.rets_df:pd.DataFrame = None

        if download:
            self.download_data()
            self.clean_data()

    def download_data(self) -> pd.DataFrame:

        # Auto adjust = false so we get both close price and adjusted close price
        # Set Actions = True if you want to grab dividen and split data as well
        
        self.raw_data_df = yf.download(self.input_tickers, group_by='ticker',auto_adjust=False,actions=False)
        return self.raw_data_df
    
    def clean_data(self) -> pd.DataFrame:

        # Copy the raw data
        adjusted_prices_df = self.raw_data_df.copy()

        # We only need the adjusted close price for each stock (which is on the second level of the columns)
        adjusted_prices_df = adjusted_prices_df.loc[:, (slice(None), 'Adj Close')]

        # We need to flatten the columns
        adjusted_prices_df.columns = adjusted_prices_df.columns.droplevel(1)

        # Forward fill NA values with last available price
        adjusted_prices_df.ffill(inplace=True)

        # Create a total return column
        self.rets_df =  adjusted_prices_df.pct_change(fill_method=None) 

        # Sort the columns alphabetically
        self.rets_df = self.rets_df[sorted(self.rets_df.columns)].copy()
        self.adjusted_prices_df = adjusted_prices_df

        return self.rets_df
    
    def __repr__(self) -> str:
        return f'DataBlob: {self.tickers}'
    
    @property
    def tickers(self) -> list[str]:
        return self.rets_df.columns.tolist()
    
    def save_data(self) -> None:
        self.rets_df.to_csv(f'{DATA_FOLDER}rets_df.csv')
        self.adjusted_prices_df.to_csv(f'{DATA_FOLDER}adjusted_prices_df.csv')

    @staticmethod
    def load_saved_data() -> "DataBlob":
        dblob = DataBlob(tickers=None,download=False)
        dblob.rets_df = pd.read_csv(f'{DATA_FOLDER}rets_df.csv',index_col=0,parse_dates=True)
        dblob.adjusted_prices_df = pd.read_csv(f'{DATA_FOLDER}adjusted_prices_df.csv',index_col=0,parse_dates=True)
        return dblob



if __name__ == '__main__':

    tickers = ['AAPL','MSFT','AMZN','GOOGL','META','TSLA','JPM']
    downloader = DataBlob(tickers)
    downloader.save_data()

