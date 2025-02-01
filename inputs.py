from dataclasses import dataclass
import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

# Add a dataclass to hold the user inputs


@dataclass
class CleanInputs:

    tickers: list
    weights_input: str
    start_date: dt.datetime
    end_date: dt.datetime
    port_name: str
    rebalance_freq: str


def get_user_inputs():
    """Collects user inputs and returns them as variables."""

    st.markdown("## User Inputs")

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

    # Date range selection dropdown
    date_option = st.selectbox(
        "Select a time range:",
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
    start_date_default = date_dict.get(date_option, prior_year_end).date()

    # Start date (users can override)
    start_date = st.date_input("Start Date (Assumes you invest at close of this date):", start_date_default)

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

    clean_inputs = CleanInputs(tickers, weights_input, start_date, end_date, port_name, rebalance_freq)

    return clean_inputs