import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt

import data_download as dd
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
# ----------------------------
# User Input Section
# ----------------------------

st.markdown("## User Inputs")

# Option to fetch new data
fetch_new_data = st.checkbox("Fetch New Data", value=False)

def get_user_inputs():
    """Fetch user inputs from Streamlit widgets."""
    

    # Ticker Input
    tickers_input = st.text_area(
        "Enter tickers separated by commas (e.g., AAPL, MSFT, AMZN, GOOGL, META, TSLA, JPM):",
        "SPY, JPM"
    )
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if not tickers:
        st.error("Please enter at least one valid ticker.")
        st.stop()

    st.markdown("#### Portfolio Weights")
    # Weights Input
    equal_weights = [1 / len(tickers)] * len(tickers)
    weights_input = st.text_area(
        "Enter weights for each ticker (comma-separated, should sum to 1):",
        ",".join(map(str, equal_weights))
    )

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

    st.markdown("#### Date Range")

    today = dt.datetime.today()
    yesterday = today - dt.timedelta(days=1)
    prior_year_end = dt.datetime(today.year - 1, 12, 31)
    one_year_ago = today.replace(year=today.year - 1)
    three_years_ago = today - dt.timedelta(days=3 * 365)

    # Date range selection dropdown
    date_option = st.selectbox(
        "Select a time range:",
        ["Custom", "1D", "YTD", "1 Year", "3 Years"]
    )


    # Auto-set dates based on selection
    # This should also set the end dates. Move all this to a dictionary?
    if date_option == "1D":
        start_date_option = yesterday - dt.timedelta(days=1)
    elif date_option == '3-Month':
        start_date_option = dt.datetime(today.year, today.month, 1)
    elif date_option == "YTD":
        start_date_option = prior_year_end
    elif date_option == "1 Year":
        start_date_option = one_year_ago
    elif date_option == "3 Years":
        start_date_option = three_years_ago
    else:
        start_date_option = prior_year_end

    start_date_option = start_date_option.date()

    start_date = st.date_input("Start Date (Assumes you invest at close of this date):", start_date_option)
    
    end_date = st.date_input("End Date (Assumes you liqudidate at close of this date))", yesterday)

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

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

    # Extract only the alias (e.g., 'B' from 'B - Business day')
    rebalance_freq = rebalance_freq.split(" - ")[0]


    port_name = st.text_input("Enter a name for your portfolio:", "Port")

    return tickers, weights, start_date, end_date, port_name, rebalance_freq

# Fetch user inputs
tickers, weights, start_date, end_date, port_name, rebalance_freq = get_user_inputs()


# ----------------------------
# Data Loading & Processing
# ----------------------------

st.markdown("## Data Processing")

# Load market data
if fetch_new_data:
    with st.spinner("Fetching new data..."):
        data = dd.DataBlob(tickers, download=True)
else:
    data = dd.DataBlob.load_saved_data()

# Ensure selected tickers exist in dataset
missing_tickers = [t for t in tickers if t not in data.tickers]
if missing_tickers:
    st.error(f"Some tickers are missing from data: {', '.join(missing_tickers)}")
    st.stop()

# Filter returns dataframe to selected tickers
data.rets_df = data.rets_df[tickers].copy()

# ----------------------------
# Backtest Execution
# ----------------------------


with st.spinner("Running backtest..."):
    backtester = bt.Backtester(
        data_blob=data,
        tickers=tickers,
        weights=weights,
        start_date=str(start_date),
        end_date=str(end_date),
        rebal_freq=rebalance_freq,
    )
    backtester.run_backtest()

# ----------------------------
# Data Visualization
# ----------------------------

st.markdown("## Results")



# Cumulative Portfolio Returns
st.subheader("Cumulative Returns")

stock_rets = data.rets_df.loc[start_date:end_date].fillna(0) # This start date might be 1 day early
cumulative_rets = (1 + stock_rets).cumprod() - 1
combo_cum_df = pd.concat([backtester.wealth_index - 1, cumulative_rets], axis=1).dropna()
combo_cum_df = combo_cum_df.rename(columns={0: "Portfolio"})

# Plot the cumulative return with the y axis as a percentage
fig1 = px.line(combo_cum_df, title="Cumulative Returns")
fig1.update_yaxes(tickformat=".2%")

st.plotly_chart(fig1)

# Add a table of cumulative returns (# How to make below prettier?) At very least it shoudl be a heat map
total_rets = (combo_cum_df.iloc[-1]*100).sort_values(ascending=False)
total_rets = pd.Series([f"{x:.2f}%" for x in total_rets], index=total_rets.index,name='Total Returns')
st.write(total_rets)

# Portfolio Weights Over Time
st.subheader("Portfolio Weights Over Time")

fig2 = px.line(backtester.weights_df, title="Portfolio Weights")
st.plotly_chart(fig2)

# ----------------------------
# Display Data Summary
# ----------------------------





st.markdown('## Raw Data Reference')

st.markdown('### Rebalance Dates')
dates = backtester.rebalance_dates
dates.name = 'Rebalance Dates'
# show as date only, not datetime
dates = pd.Series(dates.date,name='Rebalance Dates')
st.write(dates)

st.markdown('### Indvidual Returns')
st.write("Head:")
st.write(data.rets_df.head())
st.write("Tail:")
st.write(data.rets_df.tail())
st.write(data.rets_df)

st.markdown('### Portfolio History')
st.write(backtester.portfolio_history_df)

st.markdown('### Portfolio Weights')
st.write(backtester.weights_df)