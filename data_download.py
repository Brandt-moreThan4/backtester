import pandas as pd
import yfinance as yf




class DataDownloader:

    def __init__(self,tickers:list[str]):
        self.input_tickers = tickers

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
    


if __name__ == '__main__':
    tickers = ['AAPL','MSFT','AMZN','GOOGL','META']
    downloader = DataDownloader(tickers)
    print(downloader.rets_df)
    print(downloader.adjusted_prices_df)

