import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_engine as dd
import backtester as bt
import inputs
import metrics
import utils


# Utility Functions
def format_as_percent(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Format specified columns as percentages."""
    for column in columns:
        df[column] = df[column].map('{:.2%}'.format)
    return df


def plot_line_chart(df: pd.DataFrame, title: str, yaxis_title: str) -> None:
    fig = px.line(df, title=title)
    fig.update_yaxes(tickformat=".2%", title_text=yaxis_title)
    fig.update_xaxes(title_text="Date")
    st.plotly_chart(fig)


def plot_bar_chart(df: pd.Series, title: str, yaxis_title: str) -> None:
    fig = px.bar(df, title=title)
    fig.update_yaxes(tickformat=".2%", title_text=yaxis_title)
    fig.update_xaxes(title_text="")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


def display_results(backtest:bt.Backtester,data:dd.DataEngine, cleaned_inputs:inputs.CleanInputs) -> None:

    start_dt = pd.to_datetime(cleaned_inputs.start_date)

    # Security returns should be after the start date (non inclusive) and before the end date (inclusive)
    rets_filered_df = data.rets_df[data.rets_df.index > start_dt].loc[:cleaned_inputs.end_date]
    security_rets_df = rets_filered_df[cleaned_inputs.tickers]
    bench_rets = rets_filered_df[cleaned_inputs.bench_ticker]
    all_rets_df = pd.concat([backtest.port_returns, security_rets_df], axis=1)
    security_prices_df = data.price_df[data.price_df.index > start_dt].loc[:cleaned_inputs.end_date]
    security_prices_df = security_prices_df[cleaned_inputs.tickers]

    bench_rets = rets_filered_df[cleaned_inputs.bench_ticker]

    st.markdown("### Cumulative Returns")

    cum_rets_df = (1 + all_rets_df).cumprod() - 1

    plot_line_chart(cum_rets_df, "Cumulative Returns", "Cumulative Returns")
    
    # Bar plot of total return
    total_rets = cum_rets_df.iloc[-1].sort_values(ascending=False)
    plot_bar_chart(total_rets, "Total Returns", "Total Return")

    # Add on yearly returns, if we have enough data
    annual_rets = all_rets_df.resample('YE').apply(lambda x: (1 + x).prod() - 1)
    if len(annual_rets) > 1:
        st.markdown("#### Annual Returns")        
        annual_rets.index = annual_rets.index.year
        annual_rets = annual_rets.T
        # Format these returns as a heatmap each year
        annual_rets = annual_rets.style.format("{:.2%}").background_gradient(cmap='RdYlGn', axis=1)


        st.write(annual_rets)

    # Volatility
    # Display the vol in a bar chart in the same order as the total rets
    st.markdown("### Volatility")    
    total_vol = all_rets_df.std() * 252 ** 0.5

    total_vol = total_vol[total_rets.index]
    plot_bar_chart(total_vol, "Total Period Annualized Volatility", "Volatility")

    # If you have enough data, plot the rolling vol
    ROLLING_WINDOW = 252
    if len(all_rets_df) > ROLLING_WINDOW:
    
        rolling_vols = all_rets_df.rolling(window=252).std() * 252 ** 0.5
        rolling_vols = rolling_vols.dropna()
        plot_line_chart(rolling_vols, "Rolling 1-Year Volatility", "Volatility")

    #---------------------------
    # Metrics
    #---------------------------

    st.markdown("### Performance Metrics")    
    metrics_df = all_rets_df.apply(metrics.calculate_metrics, args=(bench_rets,),axis=0)
    # We want to apply lots of fun formatting to the metrics
    metrics_pretty_df = metrics_df.T.copy()
    COLS_TO_PRETTIFY = ['Total Return', 'CAGR', 'Volatility', 'Max Drawdown', 'Alpha', 'Downside Deviation']
    metrics_pretty_df = format_as_percent(metrics_pretty_df, COLS_TO_PRETTIFY)
    # Format the following columns to onlu 2 decimal places
    DECIMAL_COLS = ['Beta', 'Sharpe', 'Up Capture', 'Down Capture']
    metrics_pretty_df[DECIMAL_COLS] = metrics_pretty_df[DECIMAL_COLS].map('{:.2f}'.format)

    st.write(metrics_pretty_df)

    # ----------------------------
    # Correlation Matrix
    # ----------------------------
    st.markdown("### Correlation Matrix")
    corr = all_rets_df.corr()
    corr_pretty_df = corr.copy()
    # # corr_pretty_df = corr_pretty_df.applymap('{:.2f}'.format)
    corr_pretty_df = corr.style.format("{:.2f}").background_gradient(cmap='coolwarm', vmin=-1, vmax=1)
    st.write(corr_pretty_df)


    # Portfolio Weights Over Time
    st.markdown("### Portfolio Weights Over Time")
    plot_line_chart(backtest.weights_df, "Portfolio Weights Over Time", "Weight")


    # # Returns
    # st.markdown("### Individual Returns")
    # # Add a tab for each of the securities and show a plot of it's indivdiual cumualtive return
    # ret_tabs = st.tabs(cum_rets_df.columns.to_list())
    # for ticker, tab in zip(cum_rets_df.columns, ret_tabs):
    #     with tab:
    #         total_ret = cum_rets_df[ticker].iloc[-1]
    #         st.write(f"Total Return: {total_ret:.2%}")
    #         plot_line_chart(cum_rets_df[ticker], f"{ticker} Cumulative Return", "Cumulative Return")

    #         # Add on another bar chart that shows the return on different time periods.


    st.markdown("### Individual Prices")
    st.write('_These prices are not adjusted for splits or dividends_')
    price_tabs = st.tabs(security_prices_df.columns.to_list())
    for ticker, tab in zip(security_prices_df.columns, price_tabs):
        with tab:
            fig = px.line(security_prices_df[ticker], title=f"{ticker} Prices")
            # Format in dollars
            fig.update_yaxes(title_text="Price", tickprefix="$")
            fig.update_xaxes(title_text="Date")
            st.plotly_chart(fig)


    

    # # ----------------------------
    # # Display Raw Data
    # # ----------------------------

    st.markdown("## Raw Data Reference")

    st.markdown("### Rebalance Dates")
    dates = backtest.rebalance_dates
    dates.name = 'Rebalance Dates'
    dates = pd.Series(dates.date, name='Rebalance Dates')
    st.write(dates)



    st.markdown("### Raw Returns")
    rets_df = utils.convert_dt_index(all_rets_df)
    # Format the returns as percentages and color code them. Positive returns are green, negative are red.
    styled_df = rets_df.style.format("{:.2%}").map(utils.color_returns)
    st.write(styled_df)

    # st.markdown("### Portfolio History")
    # st.write(utils.convert_dt_index(backtest.portfolio_history_df))

    st.markdown("### Raw Portfolio Weights")
    weights_df = utils.convert_dt_index(backtest.weights_df)
    weights_df = weights_df.map('{:.2%}'.format)
    st.write(weights_df)


if __name__ == '__main__':

    data = dd.DataEngine.load_saved_data() 
    back = bt.Backtester(data_blob=data,tickers=['AAPL','MSFT'],weights=[0.5,0.5],start_date='2010-01-01',end_date='2020-01-01')

    back.run_backtest()


    cleaned_inputs = inputs.CleanInputs(tickers=['AAPL','MSFT'],weights='0.5,0.5',start_date=dt.datetime(2010,1,1),end_date=dt.datetime(2020,1,1),port_name='Portfolio',rebalance_freq='QE',fetch_new_data=False,bench_ticker='SPY')

    display_results(back,data,cleaned_inputs)