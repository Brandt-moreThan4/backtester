import pandas as pd
import datetime
import numpy as np
import data_download as dd


# General, helper variables that are used later. 
all_dates = pd.date_range(start='1900-01-01',end='2099-12-31') # Big date range to cover all reasonable dates we may include in our backtest (This is filtered later)


class Backtester:

    pretty_name = 'BaseStrategy'
    short_name = 'BaseStrat'

    def __init__(
        self,
        data_blob: dd.DataBlob,
        tickers: list[str],
        weights: list[float],
        start_date: str,
        end_date: str,
        initial_capital: float = 1_000_000,
        rebal_freq: str = 'QE',
        params: dict = {}
    ) -> None:

        self.data_blob = data_blob
        self.rets_df = data_blob.rets_df
        self.input_tickers = tickers
        self.input_weights = weights
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        self.strat_dates = all_dates[(all_dates >= start_date) & (all_dates <= end_date)] 
        self.rebalance_dates = pd.date_range(start=start_date,end=end_date,freq=rebal_freq) 
        # Make sure the end date is not included in the rebalance dates
        self.rebalance_dates = self.rebalance_dates[self.rebalance_dates != end_date]

        self.validate_data()


        self.portfolio = pd.Series(index=self.input_tickers,data=0.0)
        self.portfolio['Cash'] = initial_capital
        
        # Master dataframe to store the historical portfolio holdings
        self.portfolio_history_df = pd.DataFrame(index=self.strat_dates,columns=self.input_tickers)

        # Just a catch all for any additional parameters that may be passed in for a substrategy
        self.params = params
    
    def validate_data(self) -> None:

        # Check that the input tickers are in the data blob
        for ticker in self.input_tickers:
            if ticker not in self.data_blob.tickers:
                raise ValueError(f'Ticker {ticker} not in data blob. Please check the input tickers.')

        # Check that the input weights sum to 1
        if np.abs(np.sum(self.input_weights) - 1) > 1e-8:
            raise ValueError('Input weights do not sum to 1. Please check the input weights.')

        

    def __repr__(self) -> str:
        return f'{self.short_name}: {self.start_date} - {self.end_date}'

    @property
    def port_value(self) -> float:
        return self.portfolio.sum()

    def rebalance_to_target_weights(self,target_weights:pd.Series) -> None:
        '''Rebalance the portfolio to the target weights provided. This will implictily involve selling off any
          securities that are overweight and buying any securities that are underweight.
    
        '''
    
        # Multiply the target weights by the current portfolio value to get the target value for each security
        target_values = target_weights * self.port_value

        # Update the new portfolio with the target values 
        # (This is implicitly carrying out trades...)
        self.portfolio = target_values
        self.portfolio_history_df.loc[self.current_date] = self.portfolio
    

    def increment_portfolio_by_returns(self) -> None:
        '''Increase the portfolio value by the returns for the current date. '''

        # If there is a return for the current date, then increment the portfolio by the returns
        if self.current_date in self.rets_df.index:
            self.portfolio = self.portfolio * (1 + self.rets_df.loc[self.current_date])
            
        # Regardless of if portfolio was incremented up or not, store the current portfolio value in the history for
        #  today's date. So we always have an estimated value for the portfolio at the end of each day.
        self.portfolio_history_df.loc[self.current_date] = self.portfolio

    
    def get_target_weights(self) -> pd.Series:
        '''Get the target weights for the portfolio based on the input weights. '''

        # Create a series with the input weights and the cash weight
        target_weights = pd.Series(index=self.input_tickers,data=self.input_weights)

        return target_weights

    def run_backtest(self,verbose=False) -> None:

        # Allocate the initial capital to the target weights
        target_weights = self.get_target_weights()
        self.rebalance_to_target_weights(target_weights)

        # Iterate through all the dates in the chosen time period
        for date in self.strat_dates[1:]:
            
            # Update the current date
            self.current_date = date

            # Increment the portfolio by the returns for the current date
            self.increment_portfolio_by_returns()

            # If the current date is a rebalance date, then rebalance the portfolio
            if date in self.rebalance_dates:
                if verbose:
                    print(f'Current Time {datetime.datetime.now()} Rebalancing: {date}')
                target_weights = self.get_target_weights()
                self.rebalance_to_target_weights(target_weights)

        # Calculate some useful data based on the portfolio history
        self.calculate_data()


    def calculate_data(self) -> None:
        '''Calculate some useful data based on the portfolio history which is nice to have when analyzing results.'''
        
        self.total_port_values = self.portfolio_history_df.sum(axis=1).astype(float)
        self.weights_df = (self.portfolio_history_df.div(self.total_port_values,axis=0)).astype(float)
        self.wealth_index = self.total_port_values / self.total_port_values.iloc[0]

        self.cumulative_port_returns = self.wealth_index - 1

        # Calculate portfolio returns based on the total portfolio values
        self.portfolio_returns_all = self.total_port_values.pct_change().dropna()
        self.portfolio_returns_all.name = self.short_name

        # But also calculate a portfolio return that removes days where the portfolio return is 0, because those
        # are with 99.999% certainty just holidays.
        basically_zero_mask = np.abs(self.portfolio_returns_all - 0) < 1e-8
        self.port_returns = self.portfolio_returns_all[~basically_zero_mask].copy()



if __name__ == '__main__':
    data = dd.DataBlob.load_saved_data() 
    bt = Backtester(data_blob=data,tickers=['AAPL','MSFT'],weights=[0.5,0.5],start_date='2010-01-01',end_date='2020-01-01')
    bt.run_backtest()
    print(bt.portfolio_history_df)
