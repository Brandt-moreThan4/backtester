import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_engine as dd
import backtester as bt




def display_results(backtest:bt.Backtester) -> None:


    st.markdown("## Results")

    st.markdown("### Cumulative Returns of Portfolio")
    backtest.cumulative_port_returns

    st.dataframe(backtest.cumulative_port_returns)



# def cumu


# # Cumulative Portfolio Returns
# st.subheader("Cumulative Returns")

# stock_rets = data.rets_df.loc[st.session_state.start_date:st.session_state.end_date].fillna(0)
# cumulative_rets = (1 + stock_rets).cumprod() - 1
# combo_cum_df = pd.concat([backtester.wealth_index - 1, cumulative_rets], axis=1).dropna()
# combo_cum_df = combo_cum_df.rename(columns={0: "Portfolio"})

# # Plot the cumulative return with the y-axis as a percentage
# fig1 = px.line(combo_cum_df, title="Cumulative Returns")
# fig1.update_yaxes(tickformat=".2%")

# st.plotly_chart(fig1)

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
