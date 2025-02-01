import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_engine as dd
import backtester as bt

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
# Initialize session state variables
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False  # Track form submission
if "run_backtest" not in st.session_state:
    st.session_state.run_backtest = False  # Track backtest execution
if "date_option" not in st.session_state:
    st.session_state.date_option = "YTD"  # Default date option
if "start_date" not in st.session_state:
    st.session_state.start_date = dt.datetime.today().replace(month=1, day=1).date()  # Default YTD start date

# ----------------------------
# User Input Section with Form
# ----------------------------
st.markdown("## User Inputs")

with st.form("user_input_form"):
    # Ticker Input
    tickers_input = st.text_area(
        "Enter tickers separated by commas (e.g., AAPL, MSFT, AMZN, GOOGL, META, TSLA, JPM):",
        "SPY, JPM"
    )
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    st.markdown("#### Portfolio Weights")
    # Weights Input
    equal_weights = [1 / len(tickers)] * len(tickers)
    weights_input = st.text_area(
        "Enter weights for each ticker (comma-separated, should sum to 1):",
        ",".join(map(str, equal_weights))
    )

    # Date Selection
    today = dt.datetime.today()
    yesterday = today - dt.timedelta(days=1)
    prior_year_end = dt.datetime(today.year - 1, 12, 31)
    one_year_ago = today.replace(year=today.year - 1)
    three_years_ago = today - dt.timedelta(days=3 * 365)

    # Date range selection dropdown (triggers update in session state)
    date_option = st.selectbox(
        "Select a time range:",
        ["Custom", "1D", "YTD", "1 Year", "3 Years"],
        index=["Custom", "1D", "YTD", "1 Year", "3 Years"].index(st.session_state.date_option)
    )

    # Automatically update session state when date_option is selected
    if date_option != st.session_state.date_option:
        st.session_state.date_option = date_option
        date_dict = {
            "1D": yesterday - dt.timedelta(days=1),
            "YTD": prior_year_end,
            "1 Year": one_year_ago,
            "3 Years": three_years_ago,
        }
        st.session_state.start_date = date_dict.get(date_option, prior_year_end).date()

    # Start date (linked to session state, but still editable)
    start_date = st.date_input("Start Date (Assumes you invest at close of this date):", st.session_state.start_date)

    # End Date Selection
    end_date = st.date_input("End Date (Assumes you liquidate at close of this date):", yesterday)

    # Rebalance Frequency Selection
    st.markdown("#### Rebalancing Options")
    rebalance_freq = st.selectbox(
        "Select rebalance frequency:",
        [
            "YE - Year end",
            "YS - Year start",
            "QS - Quarter start",
            "QE - Quarter end",
            "MS - Month start",
            "ME - Month end",
            "W - Weekly",
            "D - Calendar day",
        ]
    )
    rebalance_freq = rebalance_freq.split(" - ")[0]  # Extract alias

    port_name = st.text_input("Enter a name for your portfolio:", "Port")

    # Submit button for the form
    submitted = st.form_submit_button("Submit")

# If the form is submitted, store values in session state
if submitted:
    st.session_state.form_submitted = True
    st.session_state.tickers = tickers
    st.session_state.weights = weights_input
    st.session_state.start_date = start_date  # Use session state value
    st.session_state.end_date = end_date
    st.session_state.port_name = port_name
    st.session_state.rebalance_freq = rebalance_freq
    st.success("Inputs submitted! Now click 'Run Backtest'.")

# ----------------------------
# Run Backtest Button
# ----------------------------
if st.session_state.form_submitted:
    if st.button("Run Backtest"):
        st.session_state.run_backtest = True


# ----------------------------
# Data Processing & Backtest Execution
# ----------------------------
if st.session_state.get("run_backtest", False):
    st.markdown("## Data Processing")

    # Load market data
    with st.spinner("Fetching new data..."):
        data = dd.DataEngine(st.session_state.tickers, download=True)

    # Ensure selected tickers exist in dataset
    missing_tickers = [t for t in st.session_state.tickers if t not in data.tickers]
    if missing_tickers:
        st.error(f"Some tickers are missing from data: {', '.join(missing_tickers)}")
        st.stop()

    # Filter returns dataframe to selected tickers
    data.rets_df = data.rets_df[st.session_state.tickers].copy()

    # ----------------------------
    # Backtest Execution
    # ----------------------------

    st.markdown("## Backtest Execution")

    with st.spinner("Running backtest..."):
        backtester = bt.Backtester(
            data_blob=data,
            tickers=st.session_state.tickers,
            weights=[float(w) for w in st.session_state.weights.split(",")],
            start_date=str(st.session_state.start_date),
            end_date=str(st.session_state.end_date),
            rebal_freq=st.session_state.rebalance_freq,
        )
        backtester.run_backtest()

    # ----------------------------
    # Data Visualization
    # ----------------------------

    st.markdown("## Results")

    # Cumulative Portfolio Returns
    st.subheader("Cumulative Returns")

    stock_rets = data.rets_df.loc[st.session_state.start_date:st.session_state.end_date].fillna(0)
    cumulative_rets = (1 + stock_rets).cumprod() - 1
    combo_cum_df = pd.concat([backtester.wealth_index - 1, cumulative_rets], axis=1).dropna()
    combo_cum_df = combo_cum_df.rename(columns={0: "Portfolio"})

    # Plot the cumulative return with the y-axis as a percentage
    fig1 = px.line(combo_cum_df, title="Cumulative Returns")
    fig1.update_yaxes(tickformat=".2%")

    st.plotly_chart(fig1)

    # Portfolio Weights Over Time
    st.subheader("Portfolio Weights Over Time")

    fig2 = px.line(backtester.weights_df, title="Portfolio Weights")
    st.plotly_chart(fig2)

    # ----------------------------
    # Display Data Summary
    # ----------------------------

    st.markdown("## Raw Data Reference")

    st.markdown("### Rebalance Dates")
    dates = backtester.rebalance_dates
    dates.name = 'Rebalance Dates'
    dates = pd.Series(dates.date, name='Rebalance Dates')
    st.write(dates)

    st.markdown("### Individual Returns")
    st.write("Head:")
    st.write(data.rets_df.head())
    st.write("Tail:")
    st.write(data.rets_df.tail())
    st.write(data.rets_df)

    st.markdown("### Portfolio History")
    st.write(backtester.portfolio_history_df)

    st.markdown("### Portfolio Weights")
    st.write(backtester.weights_df)
