import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_engine as dd
import backtester as bt
import inputs



def display_results(backtest:bt.Backtester,data:dd.DataEngine, cleaned_inputs:inputs.CleanInputs) -> None:


    # Security returns should be after the start date (non inclusive) and before the end date (inclusive)
    security_rets_df = data.rets_df[data.rets_df.index > pd.to_datetime(cleaned_inputs.start_date)].loc[:cleaned_inputs.end_date]
    security_rets_df = security_rets_df[cleaned_inputs.tickers]
    all_rets_df = pd.concat([backtest.port_returns, security_rets_df], axis=1)

    st.markdown("### Cumulative Returns of Portfolio")

    cum_rets_df = (1 + all_rets_df).cumprod() - 1

    # Plot the cumulative return with the y-axis as a percentage and the y labels called "Cumulative Returns"
    cumulative_returns_fig = px.line(cum_rets_df)
    cumulative_returns_fig.update_yaxes(tickformat=".2%",title_text="Cumulative Returns")
    cumulative_returns_fig.update_xaxes(title_text="Date")
    st.plotly_chart(cumulative_returns_fig)

    # Show the total cumulative return in a table
    total_rets = cum_rets_df.iloc[-1].rename('Total Return').sort_values(ascending=False)
    st.write(total_rets.apply(lambda x: f"{x:.2%}"))



    # 
    

    







# # Portfolio Weights Over Time
# st.subheader("Portfolio Weights Over Time")

# fig2 = px.line(backtester.weights_df, title="Portfolio Weights")
# st.plotly_chart(fig2)

# # ----------------------------
# # Display Data Summary
# # ----------------------------

# st.markdown("## Raw Data Reference")

# st.markdown("### Rebalance Dates")
# dates = backtester.rebalance_dates
# dates.name = 'Rebalance Dates'
# dates = pd.Series(dates.date, name='Rebalance Dates')
# st.write(dates)

# st.markdown("### Individual Returns")
# st.write("Head:")
# st.write(data.rets_df.head())
# st.write("Tail:")
# st.write(data.rets_df.tail())
# st.write(data.rets_df)

# st.markdown("### Portfolio History")
# st.write(backtester.portfolio_history_df)

# st.markdown("### Portfolio Weights")
# st.write(backtester.weights_df)


if __name__ == '__main__':

    data = dd.DataEngine.load_saved_data() 
    back = bt.Backtester(data_blob=data,tickers=['AAPL','MSFT'],weights=[0.5,0.5],start_date='2010-01-01',end_date='2020-01-01')

    back.run_backtest()


    cleaned_inputs = inputs.CleanInputs(tickers=['AAPL','MSFT'],weights_input='0.5,0.5',start_date=dt.datetime(2010,1,1),end_date=dt.datetime(2020,1,1),port_name='Portfolio',rebalance_freq='QE',fetch_new_data=False)

    display_results(back,data,cleaned_inputs)