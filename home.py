import pandas as pd
import streamlit as st
import plotly.express as px

import data_download as dd
import backtester as bt

st.title("Portfolio Backtester")

DOWNLOAD_DATA = False
# DOWNLOAD_DATA = True

# Load the data
data = dd.DataBlob.load_saved_data()

# User input for tickers
tickers_input = st.text_area(
    "Enter tickers separated by commas (e.g., AAPL, MSFT, AMZN, GOOGL, META, TSLA, JPM):",
    "AAPL,MSFT,AMZN,GOOGL,META,TSLA,JPM"
)

# Process tickers input
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# Ensure at least one valid ticker
if not tickers:
    st.error("Please enter at least one valid ticker.")
    st.stop()


# Pull the data for the selected tickers
if DOWNLOAD_DATA:
    data = dd.DataBlob(tickers=tickers, download=True)
    # data.save_data()

data.rets_df = data.rets_df[tickers].copy()

# User input for weights (optional)
equal_weights = [1 / len(tickers)] * len(tickers)
weights_input = st.text_input(
    f"Enter weights for each ticker (comma-separated, should sum to 1):",
    ",".join(map(str, equal_weights))
)

# Process weights input
try:
    weights = [float(w.strip()) for w in weights_input.split(",")]
    if len(weights) != len(tickers):
        st.error("Number of weights must match number of tickers.")
        st.stop()
    if abs(sum(weights) - 1.0) > 0.001:
        st.error("Weights must sum to 1.")
        st.stop()
except ValueError:
    st.error("Invalid weights. Please enter numeric values.")
    st.stop()

# User input for start and end date
start_date = st.date_input("Start Date", pd.to_datetime("2010-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2020-01-01"))

# Validate date range
if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Run backtest
backtester = bt.Backtester(
    data_blob=data,
    tickers=tickers,
    weights=weights,
    start_date=str(start_date),
    end_date=str(end_date),
)
backtester.run_backtest()

# Display cumulative returns of the portfolio

stock_rets = data.rets_df[tickers].fillna(0)
cumulative_rets = (1 + stock_rets).cumprod() - 1
combo_cum_df = pd.concat([backtester.wealth_index,cumulative_rets], axis=1).dropna(axis=0)


fig1 = px.line(combo_cum_df, title="Cumulative Returns of Portfolio")
st.plotly_chart(fig1)



# Display portfolio weights over time
fig2 = px.line(backtester.weights_df, title="Portfolio Weights")
st.plotly_chart(fig2)


st.write("Data Summary:")
st.write(data.rets_df)
st.write(backtester.portfolio_history_df)
