import pandas as pd
import streamlit as st
import plotly.express as px

import data_download as dd
import backtester as bt

st.write('Hola!!')



data = dd.DataBlob.load_saved_data()

tickers = ['AAPL','MSFT','AMZN','GOOGL','META','TSLA','JPM']
equal_weights = [1/len(tickers)]*len(tickers)
backtester = bt.Backtester(data_blob=data,tickers=tickers,weights=equal_weights,start_date='2010-01-01',end_date='2020-01-01')
backtester.run_backtest()

# Display a bunch of good data
# st.write(backtester.portfolio_history_df)
# st.write(backtester.weights_df)
# st.write(backtester.wealth_index)


# Display the cumulative returns of the portfolio
fig = px.line(backtester.wealth_index,title='Cumulative Returns of Portfolio')

st.plotly_chart(fig)

# Display the weights of the portfolio
fig = px.line(backtester.weights_df,title='Portfolio Weights')
st.plotly_chart(fig)




print('Hola!!')
