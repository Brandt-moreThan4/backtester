from dataclasses import dataclass
import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

# Add a dataclass to hold the user inputs


@dataclass
class CleanInputs:

    tickers: list
    weights: str
    start_date: dt.datetime
    end_date: dt.datetime
    port_name: str
    rebalance_freq: str
    fetch_new_data: bool = False


def get_user_inputs():
    """Collects user inputs and returns them as variables."""

    st.markdown("## User Inputs")

    # Add a toggle to fetch new date or use old
    fetch_new_data = st.toggle("Query Updated Data", value=False)
    st.write("If you want to fetch new data, toggle the switch above... Please be cautious.")

    # ------------------
    # Ticker Input
    # ------------------

    st.markdown("#### Tickers")
    tickers_input = st.text_area(
        "Enter tickers separated by spaces (e.g., AAPL MSFT AMZN GOOGL META TSLA JPM):",
        "SPY JPM"
    )

    tickers = [t.strip().upper() for t in tickers_input.split(" ") if t.strip()]

    # ------------------
    # Weights Input
    # ------------------
    st.markdown("#### Portfolio Weights")

    equal_weights = [1 / len(tickers) * 100]  * len(tickers)
    equal_weights = [f'{round(w, 2)}' for w in equal_weights]
    equal_weights_str = " ".join(equal_weights)
    weights_msg = "Enter weights for each ticker (space-separated, as percentagses should sum to 1, e.g, 35 25 40:"
    weights_input = st.text_area(
        weights_msg,
        equal_weights_str
    )

    weights_input = [float(w)/100 for w in weights_input.split(" ")]

    # Validat that weights are closish to 1

    DIFF_THRESHOLD = .05
    if abs(1 - sum(weights_input)) > DIFF_THRESHOLD:
        st.error(f"Your weights do not sum to 1. Please ensure they sum to 1. Current sum: {sum(weights_input)}")
        st.stop()

    # ------------------
    # Date Selection
    # ------------------

    st.markdown("#### Date Range")
    today = dt.datetime.today()
    yesterday = today - dt.timedelta(days=1)
    prior_year_end = dt.datetime(today.year - 1, 12, 31)
    one_year_ago = yesterday.replace(year=today.year - 1) - dt.timedelta(days=1)
    three_years_ago = yesterday.replace(year=today.year - 3) - dt.timedelta(days=1)

    # Date range selection dropdown
    date_option = st.selectbox(
        "Select a time range (assists in picking start date):",
        ["Custom", "1D", "YTD", "1 Year", "3 Years"],
        index=2,  # Default to "YTD"
    )

    # Automatically update start date based on selection
    date_dict = {
        "1D": yesterday - dt.timedelta(days=1),
        "YTD": prior_year_end,
        "1 Year": one_year_ago,
        "3 Years": three_years_ago,
    }


    start_date_default = date_dict.get(date_option,None)
    if start_date_default is None:
        # If the default is none, put whatever the last date is
        start_date_default = yesterday

    # Start date (users can override)
    start_date = st.date_input("Start Date (Assumes you invest at close of this date):", start_date_default)

    # End Date Selection
    # if date_option != 'Custom':
    end_date = st.date_input("End Date (Assumes you liquidate at close of this date):", yesterday)
    # else:
    #     end_date = st.date_input("End Date (Assumes you liquidate at close of this date):")
    # ------------------
    # Rebalance Frequency Selection
    # ------------------

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

    clean_inputs = CleanInputs(tickers, weights_input, start_date, end_date, port_name, rebalance_freq,fetch_new_data)

    return clean_inputs