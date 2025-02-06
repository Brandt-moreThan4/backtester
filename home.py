import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import inputs
import data_engine as dd
import backtester as bt
import results as rs

st.title("Portfolio Backtester")
html_title = """
<h4 style="font-family: 'Arial', sans-serif; font-size: 1.2rem; font-weight: bold; font-style: italic; color: #555; margin-top: -10px; margin-bottom: 20px; text-shadow: 1px 1px #ddd;">A Brandt Green Production</h4>
"""
st.markdown(html_title, unsafe_allow_html=True)

st.sidebar.markdown("## Table of Contents")
st.sidebar.markdown("""
- [Inputs](#inputs)
- [Results](#results)
  - [Cumulative Returns](#cumulative-returns)
  - [Volatility](#volatility)    
  - [Performance Metrics](#performance-metrics)                
  - [Correlation Matrix](#correlation-matrix)                                        
  - [Portfolio Weights Over Time](#portfolio-weights-over-time)
  - [Individual Prices](#individual-prices)
- [Raw Data Reference](#raw-data-reference)
  - [Rebalance Dates](#rebalance-dates)                    
  - [Raw Returns](#raw-returns)
  - [Raw Port Weights](#raw-portfolio-weights)
""", unsafe_allow_html=True)




# ----------------------------
# Collect User Inputs
# ----------------------------

cleaned_inputs = inputs.get_user_inputs()

# run_backtest = st.button("Run Backtest")


# ----------------------------
# Fetch Market Data & Validate against Inputs
# ----------------------------

needed_tickers = list(dict.fromkeys(cleaned_inputs.tickers + [cleaned_inputs.bench_ticker]))


# Need to uncomment out below in a bit
# if not run_backtest:
#     st.stop()


with st.spinner("Fetching data..."):
    data = dd.DataEngine()
    
    # Try loading cached data first
    data.raw_data_df = data.load_local_data(needed_tickers)
    
    # May need to review below to fetch data for any new tickers
    if data.raw_data_df is None or cleaned_inputs.fetch_new_data:
        # st.warning("Fetching new data from Yahoo Finance. This may take a second...")
        with st.spinner("Fetching new data from Yahoo Finance. This may take a second..."):
            data.download_new_data(needed_tickers)
    
    # Make sure it's been cleaned
    data.clean_data()


# Validate we have the data to run a backtest
# Ensure selected tickers exist in dataset (Should be moved somewhere else???)
missing_tickers = [t for t in cleaned_inputs.tickers if t not in data.tickers]
if missing_tickers:
    error_msg = f"""Missing data for some tickers. Sorry... If you want to fetch new data, toggle the buttom
\n Missing tickers: {missing_tickers}"""
    st.error(error_msg)
    st.stop()


# Filter returns dataframe for only the selected tickers
data.rets_df = data.rets_df[needed_tickers].copy()



# Check that we have returns for all tickers for the entire backtest period
missing_returns = data.rets_df.loc[cleaned_inputs.start_date:cleaned_inputs.end_date].isnull().sum()
if missing_returns.any():
    error_msg = f"""Missing returns for some tickers during the backtest period. Sorry... 
\n Problem tickers: {missing_returns[missing_returns > 0].index.tolist()}"""
    st.error(error_msg)
    st.stop()



# ----------------------------
# Run Backtest
# ----------------------------

with st.spinner("Running backtest..."):
    backtester = bt.Backtester(
        data_blob=data,
        tickers=cleaned_inputs.tickers,
        weights=cleaned_inputs.weights,
        start_date=str(cleaned_inputs.start_date),
        end_date=str(cleaned_inputs.end_date),
        rebal_freq=cleaned_inputs.rebalance_freq,
    )
    backtester.run_backtest()

# ----------------------------
# Display Results
# ----------------------------

# Add a few line breaks and a separator to distinguish the results section
st.markdown("---")
st.markdown("## Results")

rs.display_results(backtester, data, cleaned_inputs)
