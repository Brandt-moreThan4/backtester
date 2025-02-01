import pandas as pd
import yfinance as yf
import constants as C

DATA_FOLDER = 'data/'


# Later I need to implement some better caching mechanisms to avoid downloading the same data over and over again

class DataEngine:

    def __init__(self) -> None:
        self.adjusted_prices_df:pd.DataFrame = None
        self.rets_df:pd.DataFrame = None
        self.price_df:pd.DataFrame = None
        self.raw_data_df:pd.DataFrame = None


    def download_new_data(self,tickers:list[str]) -> pd.DataFrame:

        # Auto adjust = false so we get both close price and adjusted close price
        # Set Actions = True if you want to grab dividen and split data as well
        
        self.raw_data_df = yf.download(tickers, group_by='ticker',auto_adjust=False,actions=False)
        self.clean_data()
        
        return self.rets_df
    
    def clean_data(self) -> pd.DataFrame:

        # Copy the raw data
        df = self.raw_data_df.copy()

        df.index = pd.to_datetime(df.index)

        self.price_df = df.loc[:, (slice(None), 'Close')]
        self.price_df.columns = self.price_df.columns.droplevel(1)

        # We only need the adjusted close price for each stock (which is on the second level of the columns)
        adjusted_prices_df = df.loc[:, (slice(None), 'Adj Close')].copy()

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
        self.price_df.to_csv(f'{DATA_FOLDER}price_df.csv')
                 

    @staticmethod
    def load_saved_data() -> "DataEngine":
        dblob = DataEngine()
        dblob.rets_df = pd.read_csv(f'{DATA_FOLDER}rets_df.csv',index_col=0,parse_dates=True)
        dblob.adjusted_prices_df = pd.read_csv(f'{DATA_FOLDER}adjusted_prices_df.csv',index_col=0,parse_dates=True)
        dblob.price_df = pd.read_csv(f'{DATA_FOLDER}price_df.csv',index_col=0,parse_dates=True)
        dblob.price_df.index = pd.to_datetime(dblob.price_df.index)

        return dblob



if __name__ == '__main__':


    
    downloader = DataEngine()


    #------ Load saved data
    downloader.load_saved_data()

    #------ Downloading new Data

    # downloader.download_new_data(C.ALL_TICKERS)
    # downloader.download_new_data(C.MARKET_TICKERS)
    # downloader.clean_data() 
    

    # downloader.save_data()

