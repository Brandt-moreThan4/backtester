from dataclasses import dataclass
import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt
import constants as C

# Add a dataclass to hold the user inputs


@dataclass
class CleanInputs:

    tickers: list
    weights: str
    start_date: dt.datetime
    end_date: dt.datetime
    port_name: str
    rebalance_freq: str
    bench_ticker: str
    fetch_new_data: bool = False


today = dt.datetime.today()
yesterday = today - dt.timedelta(days=1)
day_before_yesterday = today - dt.timedelta(days=2)
prior_year_end = dt.datetime(today.year - 1, 12, 31)
one_year_ago = yesterday.replace(year=today.year - 1) - dt.timedelta(days=1)
three_years_ago = yesterday.replace(year=today.year - 3) - dt.timedelta(days=1)
five_years_ago = yesterday.replace(year=today.year - 5) - dt.timedelta(days=1)
ten_years_ago = yesterday.replace(year=today.year - 10) - dt.timedelta(days=1)
fifteen_years_ago = yesterday.replace(year=today.year - 15) - dt.timedelta(days=1)


def get_user_inputs():
    """Collects user inputs and returns them as variables."""

    st.markdown("## Inputs")

    # ------------------
    # Ticker Input
    # ------------------

    st.markdown("#### Tickers")
    default_ticks = ' '.join(C.SECTOR_TICKERS)
    tickers_input = st.text_area(
        "Enter tickers separated by spaces (e.g., AAPL MSFT AMZN GOOGL META TSLA JPM):",
        default_ticks
    )

    tickers = [t.strip().upper() for t in tickers_input.split(" ") if t.strip()]

    TICKER_LIMIT = 50
    if len(tickers) > TICKER_LIMIT:
        st.error(f'Sorry, for now the maximum tickers allowed is {TICKER_LIMIT}. Because I am worried about abusing the API. ')
        st.stop()

    # Raise error if there are duplicates
    if len(tickers) != len(set(tickers)):
        dups = set([ticker for ticker in tickers if tickers.count(ticker) > 1])
        st.error(f"Duplicate tickers found. Please remove: {dups}")

    # ------------------
    # Weights Input
    # ------------------
    st.markdown("#### Portfolio Weights")

    equal_weights = [1 / len(tickers) * 100]  * len(tickers)
    equal_weights = [f'{round(w, 2)}' for w in equal_weights]
    equal_weights_str = " ".join(equal_weights)
    weights_msg = "Enter the target weights for each ticker. Defaults to equal-weight. Space-separated. Percentagses. Should sum to 1, e.g, 35 25 40:"
    weights_input = st.text_area(
        weights_msg,
        equal_weights_str
    )

    weights_input = weights_input.split(" ")
    # Make sure the number of weights matches the number of tickers
    if len(weights_input) != len(tickers):
        st.error(f"Number of weights does not match number of tickers. Please provide a weight for each ticker.")
        st.stop()

    # Convert to floats
    weights_input = [float(w)/100 for w in weights_input]

    # Validat that weights are closish to 1

    DIFF_THRESHOLD = .05
    if abs(1 - sum(weights_input)) > DIFF_THRESHOLD:

        st.error(f"Your weights do not sum to 1. Please ensure they sum to 1. Current sum: {sum(weights_input)}")
        st.stop()
    
    # Rescale the weights anyway (to handle when they are super close)
    weights_input = [w / sum(weights_input) for w in weights_input]

    # ------------------
    # Date Selection
    # ------------------

    st.markdown("#### Date Range")

    # Date range selection dropdown
    date_option = st.selectbox(
        "Select a time range (assists in picking start date):",
        ["Custom", "1D", "YTD", "1 Year", "3 Years", "5 Years", "10 Years", "15 Years"],
        index=2,  # Default to "YTD"
    )

    # Automatically update start date based on selection
    date_dict = {
        "1D": day_before_yesterday,
        "YTD": prior_year_end,
        "1 Year": one_year_ago,
        "3 Years": three_years_ago,
        "5 Years": five_years_ago,
        "10 Years": ten_years_ago,
        "15 Years": fifteen_years_ago,
    }


    start_date_default = date_dict.get(date_option,None)
    if start_date_default is None:
        # If the default is none, 
        start_date_default = day_before_yesterday

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
        ],
        index=3  # Default to "QE - Quarter end"
    )

    rebalance_freq = rebalance_freq.split(" - ")[0]  # Extract alias


    # ------------------
    # Benchmark Selection
    # ------------------
    st.markdown("#### Benchmark")
    benchmark = st.selectbox(
        "Select a benchmark:",
        ["SPY", "IWM","QQQ","BND"],
        index=0
    )



    # ------------------
    # Portfolio Name
    # ----------------
    port_name = st.text_input("Enter a name for your portfolio:", "Port")
    st.markdown('---')

    # Add a toggle to fetch new date or use old
    fetch_new_data = st.toggle("Query Updated Data", value=False)
    st.write("If you want to fetch new data, toggle the switch above... Please be cautious.")
    
    
    clean_inputs = CleanInputs(
        tickers=tickers,
        weights=weights_input,
        start_date=start_date,
        end_date=end_date,
        port_name=port_name,
        rebalance_freq=rebalance_freq,
        bench_ticker=benchmark,
        fetch_new_data=fetch_new_data
    )
    return clean_inputs