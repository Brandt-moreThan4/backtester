import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_engine as dd
import backtester as bt
import inputs
import metrics
import utils

def display_results(backtest:bt.Backtester,data:dd.DataEngine, cleaned_inputs:inputs.CleanInputs) -> None:

    start_dt = pd.to_datetime(cleaned_inputs.start_date)

    # Security returns should be after the start date (non inclusive) and before the end date (inclusive)
    rets_filered_df = data.rets_df[data.rets_df.index > start_dt].loc[:cleaned_inputs.end_date]
    security_rets_df = rets_filered_df[cleaned_inputs.tickers]
    all_rets_df = pd.concat([backtest.port_returns, security_rets_df], axis=1)
    security_prices_df = data.price_df[data.price_df.index > start_dt].loc[:cleaned_inputs.end_date]
    security_prices_df = security_prices_df[cleaned_inputs.tickers]

    bench_rets = rets_filered_df[cleaned_inputs.bench_ticker]

    st.markdown("### Cumulative Returns of Portfolio")

    cum_rets_df = (1 + all_rets_df).cumprod() - 1

    # Plot the cumulative return with the y-axis as a percentage and the y labels called "Cumulative Returns"
    cumulative_returns_fig = px.line(cum_rets_df)
    cumulative_returns_fig.update_yaxes(tickformat=".2%",title_text="Cumulative Returns")
    cumulative_returns_fig.update_xaxes(title_text="Date")
    st.plotly_chart(cumulative_returns_fig)
    
    # Bar plot of total return
    total_rets = cum_rets_df.iloc[-1].sort_values(ascending=False)
    tot_ret_fig = px.bar(total_rets, title="Total Returns")
    tot_ret_fig.update_yaxes(tickformat=".2%",title_text="Total Return")
    # Remove the x-axis title
    tot_ret_fig.update_xaxes(title_text="")
    # Remove the legend
    tot_ret_fig.update_layout(showlegend=False)
    st.plotly_chart(tot_ret_fig)

    # Volatility
    st.markdown("### Volatility")
    total_vol = all_rets_df.std() * 252 ** 0.5
    # Display the vol in a bar chart in the same order as the total rets
    total_vol = total_vol[total_rets.index]
    vol_fig = px.bar(total_vol, title="Total Period Annualized Volatility")
    vol_fig.update_yaxes(tickformat=".2%",title_text="Volatility")
    # Remove the x-axis title
    vol_fig.update_xaxes(title_text="")
    # Remove the legend
    vol_fig.update_layout(showlegend=False)
    st.plotly_chart(vol_fig)

    # If you have enough data, plot the rolling vol
    ROLLING_WINDOW = 252
    if len(all_rets_df) > ROLLING_WINDOW:
            
        rolling_vols = all_rets_df.rolling(window=252).std() * 252 ** 0.5
        rolling_vols = rolling_vols.dropna()
        vol_fig = px.line(rolling_vols, title='Rolling 1-Year Volatility')
        vol_fig.update_yaxes(tickformat=".2%",title_text="Volatility")
        st.plotly_chart(vol_fig) 

    # Metrics

    st.markdown("### Performance Metrics")    
    metrics_df = all_rets_df.apply(metrics.calculate_metrics, args=(bench_rets,),axis=0)
    # We want to apply lots of fun formatting to the metrics
    metrics_pretty_df = metrics_df.T.copy()
    metrics_pretty_df['Total Return'] = metrics_pretty_df['Total Return'].map('{:.2%}'.format)
    metrics_pretty_df['CAGR'] = metrics_pretty_df['CAGR'].map('{:.2%}'.format)
    metrics_pretty_df['Volatility'] = metrics_pretty_df['Volatility'].map('{:.2%}'.format)
    metrics_pretty_df['Sharpe'] = metrics_pretty_df['Sharpe'].map('{:.2f}'.format)
    metrics_pretty_df['Max Drawdown'] = metrics_pretty_df['Max Drawdown'].map('{:.2%}'.format)
    metrics_pretty_df['Beta'] = metrics_pretty_df['Beta'].map('{:.2f}'.format)
    metrics_pretty_df['Alpha'] = metrics_pretty_df['Alpha'].map('{:.2%}'.format)
    metrics_pretty_df['Downside Deviation'] = metrics_pretty_df['Downside Deviation'].map('{:.2%}'.format)
    metrics_pretty_df['Up Capture'] = metrics_pretty_df['Up Capture'].map('{:.2f}'.format)
    metrics_pretty_df['Down Capture'] = metrics_pretty_df['Down Capture'].map('{:.2f}'.format)

    # Apply heat map to CAGR column

    st.write(metrics_pretty_df)

    # Portfolio Weights Over Time
    st.markdown("### Portfolio Weights Over Time")
    fig2 = px.line(backtest.weights_df)
    # fig2.update_yaxes(tickformat=".2%", title_text="Weight", range=[0, 1]) 
    fig2.update_yaxes(tickformat=".2%", title_text="Weight")    
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

            # Add on another bar chart that shows the return on different time periods.
            total_ret = cum_rets_df[ticker].iloc[-1]
            st.write(f"Total Return: {total_ret:.2%}")

    st.markdown("### Individual Prices")
    st.write('_Prices are not adjusted for splits or dividends_')
    price_tabs = st.tabs(security_prices_df.columns.to_list())
    for ticker, tab in zip(security_prices_df.columns, price_tabs):
        with tab:
            fig = px.line(security_prices_df[ticker], title=f"{ticker} Prices")
            fig.update_yaxes(title_text="Price")
            fig.update_xaxes(title_text="Date")
            st.plotly_chart(fig)


 




    # # ----------------------------
    # # Display Data Summary
    # # ----------------------------

    st.markdown("## Raw Data Reference")

    st.markdown("### Rebalance Dates")
    dates = backtest.rebalance_dates
    dates.name = 'Rebalance Dates'
    dates = pd.Series(dates.date, name='Rebalance Dates')
    st.write(dates)

    def color_returns(val):
        color = "green" if val > 0 else "red"
        return f"color: {color}"

    st.markdown("### Raw Returns")
    rets_df = utils.convert_dt_index(security_rets_df)
    # Format the returns as percentages and color code them. Positive returns are green, negative are red.
    styled_df = rets_df.style.format("{:.2%}").applymap(color_returns)
    st.write(styled_df)

    st.markdown("### Portfolio History")
    st.write(utils.convert_dt_index(backtest.portfolio_history_df))

    st.markdown("### Raw Portfolio Weights")
    weights_df = utils.convert_dt_index(backtest.weights_df)
    weights_df = weights_df.applymap('{:.2%}'.format)
    st.write(weights_df)


if __name__ == '__main__':

    data = dd.DataEngine.load_saved_data() 
    back = bt.Backtester(data_blob=data,tickers=['AAPL','MSFT'],weights=[0.5,0.5],start_date='2010-01-01',end_date='2020-01-01')

    back.run_backtest()


    cleaned_inputs = inputs.CleanInputs(tickers=['AAPL','MSFT'],weights='0.5,0.5',start_date=dt.datetime(2010,1,1),end_date=dt.datetime(2020,1,1),port_name='Portfolio',rebalance_freq='QE',fetch_new_data=False,bench_ticker='SPY')

    display_results(back,data,cleaned_inputs)