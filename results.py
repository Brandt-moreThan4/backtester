import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_engine as dd
import backtester as bt
import inputs



def display_results(backtest:bt.Backtester,data:dd.DataEngine, cleaned_inputs:inputs.CleanInputs) -> None:

    start_dt = pd.to_datetime(cleaned_inputs.start_date)

    # Security returns should be after the start date (non inclusive) and before the end date (inclusive)
    security_rets_df = data.rets_df[data.rets_df.index > start_dt].loc[:cleaned_inputs.end_date]
    security_rets_df = security_rets_df[cleaned_inputs.tickers]
    all_rets_df = pd.concat([backtest.port_returns, security_rets_df], axis=1)
    security_prices_df = data.price_df[data.price_df.index > start_dt].loc[:cleaned_inputs.end_date]
    security_prices_df = security_prices_df[cleaned_inputs.tickers]
    st.markdown("### Cumulative Returns of Portfolio")

    cum_rets_df = (1 + all_rets_df).cumprod() - 1

    # Plot the cumulative return with the y-axis as a percentage and the y labels called "Cumulative Returns"
    cumulative_returns_fig = px.line(cum_rets_df)
    cumulative_returns_fig.update_yaxes(tickformat=".2%",title_text="Cumulative Returns")
    cumulative_returns_fig.update_xaxes(title_text="Date")
    st.plotly_chart(cumulative_returns_fig)



    # Portfolio Weights Over Time
    st.markdown("### Portfolio Weights Over Time")
    fig2 = px.line(backtest.weights_df)
    fig2.update_yaxes(tickformat=".2%",title_text="Weight")
    fig2.update_xaxes(title_text="Date")
    st.plotly_chart(fig2)


    # Returns
    st.markdown("### Individual Returns")
    # Add a tab for each of the securities and show a plot of it's indivdiual cumualtive return
    ret_tabs = st.tabs(cum_rets_df.columns.to_list())
    for ticker, tab in zip(cum_rets_df.columns, ret_tabs):
        with tab:
            fig = px.line(cum_rets_df[ticker], title=f"{ticker} Cumulative Return")
            fig.update_yaxes(tickformat=".2%",title_text="Cumulative Return")
            fig.update_xaxes(title_text="Date")
            st.plotly_chart(fig)

    st.markdown("### Individual Prices")
    st.write('_Prices are not adjusted for splits or dividends_')
    price_tabs = st.tabs(security_prices_df.columns.to_list())
    for ticker, tab in zip(security_prices_df.columns, price_tabs):
        with tab:
            fig = px.line(security_prices_df[ticker], title=f"{ticker} Prices")
            fig.update_yaxes(title_text="Price")
            fig.update_xaxes(title_text="Date")
            st.plotly_chart(fig)

    # Prices


    # Metrics
    st.markdown("### Portfolio Metrics")
    # Show the total cumulative return in a table
    total_rets = cum_rets_df.iloc[-1].rename('Total Return').sort_values(ascending=False)
    st.write(total_rets.apply(lambda x: f"{x:.2%}"))




    # # ----------------------------
    # # Display Data Summary
    # # ----------------------------

    st.markdown("## Raw Data Reference")

    st.markdown("### Rebalance Dates")
    dates = backtest.rebalance_dates
    dates.name = 'Rebalance Dates'
    dates = pd.Series(dates.date, name='Rebalance Dates')
    st.write(dates)

    st.markdown("### Individual Returns")
    # st.write("Head:")
    # st.write(data.rets_df.head())
    # st.write("Tail:")
    # st.write(data.rets_df.tail())
    st.write(all_rets_df)

    st.markdown("### Portfolio History")
    st.write(backtest.portfolio_history_df)

    st.markdown("### Port Weights")
    st.write(backtest.weights_df)


if __name__ == '__main__':

    data = dd.DataEngine.load_saved_data() 
    back = bt.Backtester(data_blob=data,tickers=['AAPL','MSFT'],weights=[0.5,0.5],start_date='2010-01-01',end_date='2020-01-01')

    back.run_backtest()


    cleaned_inputs = inputs.CleanInputs(tickers=['AAPL','MSFT'],weights='0.5,0.5',start_date=dt.datetime(2010,1,1),end_date=dt.datetime(2020,1,1),port_name='Portfolio',rebalance_freq='QE',fetch_new_data=False)

    display_results(back,data,cleaned_inputs)