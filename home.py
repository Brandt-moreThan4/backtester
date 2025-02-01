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
- [User Inputs](#user-inputs)
- [Data Processing](#data-processing)
- [Results](#results)
  - [Cumulative Returns](#cumulative-returns-of-portfolio)
  - [Portfolio Weights](#portfolio-weights-over-time)
- [Raw Data Reference](#raw-data-reference)
  - [Rebalance Dates](#rebalance-dates)
  - [Individual Returns](#individual-returns)
  - [Portfolio History](#portfolio-history)
  - [Portfolio Weights](#portfolio-weights)
""", unsafe_allow_html=True)


# ----------------------------
# Collect User Inputs
# ----------------------------

cleaned_inputs = inputs.get_user_inputs()



# ----------------------------
# Fetch Market Data
# ----------------------------
with st.spinner("Fetching new data..."):
    data = dd.DataEngine()
    data = dd.DataEngine.load_saved_data()

# ----------------------------
# Data Validation
# ----------------------------

# Ensure selected tickers exist in dataset
missing_tickers = [t for t in cleaned_inputs.tickers if t not in data.tickers]
if missing_tickers:
    st.error(f"Some tickers are missing from data: {', '.join(missing_tickers)}")
    st.stop()

# Filter returns dataframe for only the selected tickers
data.rets_df = data.rets_df[cleaned_inputs.tickers].copy()

# ----------------------------
# Run Backtest
# ----------------------------

run_backtest = st.button("Run Backtest")

if not run_backtest:
    st.stop()


# ----------------------------
# Backtest Execution
# ----------------------------

with st.spinner("Running backtest..."):
    backtester = bt.Backtester(
        data_blob=data,
        tickers=cleaned_inputs.tickers,
        weights=[float(w) for w in cleaned_inputs.weights_input.split(",")],
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

rs.display_results(backtester)
