import pandas as pd
import statsmodels.formula.api as smf
import numpy as np

def calculate_beta(rets:pd.Series,bench_rets:pd.Series) -> float:
    '''Calculate the beta of the portfolio returns against the benchmark returns.'''
    
    # Join series together to have matching dates
    both_rets = pd.concat([rets,bench_rets],axis=1).dropna()

    cov_matrix = both_rets.cov()
    beta = cov_matrix.iloc[0,1] / cov_matrix.iloc[1,1]

    return beta

def calculate_alpha(returns:pd.Series,bench_rets:pd.Series) -> float:
    '''Calculate annualzied alpha.'''

    # Create a cleaneddataframe so we can feed it into statsmodels
    data = pd.concat([returns,bench_rets],axis=1).dropna()
    data.columns = ['port','bench']
    model = smf.ols('port ~ bench',data=data).fit()
    alpha = model.params['Intercept'] * 252

    return alpha


def upside_capture(port_rets: pd.Series, bench_rets: pd.Series) -> float:
    '''Calculate the upside capture ratio using average returns.'''
    
    # Join series together to align dates
    both_rets = pd.concat([port_rets, bench_rets], axis=1).dropna()
    up_market_rets = both_rets[both_rets.iloc[:, 1] > 0]  # Use only periods where the benchmark is positive

    # Calculate average returns
    port_avg_ret = up_market_rets.iloc[:, 0].mean()
    bench_avg_ret = up_market_rets.iloc[:, 1].mean()

    # Avoid division by zero
    if bench_avg_ret == 0:
        return np.nan

    # Calculate upside capture ratio
    up_capture = port_avg_ret / bench_avg_ret
    return up_capture


def downside_capture(port_rets: pd.Series, bench_rets: pd.Series) -> float:
    '''Calculate the downside capture ratio using average returns.'''
    
    # Join series together to align dates
    both_rets = pd.concat([port_rets, bench_rets], axis=1).dropna()
    down_market_rets = both_rets[both_rets.iloc[:, 1] < 0]  # Use only periods where the benchmark is negative

    # Calculate average returns
    port_avg_ret = down_market_rets.iloc[:, 0].mean()
    bench_avg_ret = down_market_rets.iloc[:, 1].mean()

    # Avoid division by zero
    if bench_avg_ret == 0:
        return np.nan

    # Calculate downside capture ratio
    down_capture = port_avg_ret / bench_avg_ret
    return down_capture


def get_downside_deviation(returns, target=0):
    downside_diff = np.maximum(0, target - returns)
    squared_diff = np.square(downside_diff)
    mean_squared_diff = np.nanmean(squared_diff)
    dd = np.sqrt(mean_squared_diff) * np.sqrt(252)
    return dd


def get_max_drawdown(returns:pd.Series) -> float:

    wealth_index = (1 + returns).cumprod().array

    # Insert a wealth index of 1 at the beginning to make the calculation work
    wealth_index = np.insert(wealth_index,0,1)
    # Get the cumulative max
    cum_max = np.maximum.accumulate(wealth_index)
    max_dd = ((wealth_index / cum_max) - 1).min()

    return max_dd


def calculate_metrics(returns:pd.Series,bench_rets:pd.Series) -> dict:
    '''Calculate the key metrics for a given series of returns. Assumes returns are daily.'''

    total_ret = (1+returns).prod() - 1
    cagr = (total_ret + 1) ** (252 / returns.shape[0]) - 1
    vol = returns.std() * np.sqrt(252)
    max_dd = get_max_drawdown(returns)

    # Sharpe Ratio
    sharpe = returns.mean() / returns.std() * np.sqrt(252)
    alpha = calculate_alpha(returns,bench_rets)


    beta = calculate_beta(returns,bench_rets)
    downside_deviation = get_downside_deviation(returns)

    up_capture = upside_capture(returns,bench_rets)
    down_capture = downside_capture(returns,bench_rets)

    metrics = {
        'Total Return': total_ret,
        'CAGR': cagr,
        'Volatility': vol,
        'Sharpe': sharpe,
        'Max Drawdown': max_dd,
        'Beta': beta,
        'Alpha': alpha,
        'Downside Deviation': downside_deviation,
        'Up Capture': up_capture,
        'Down Capture': down_capture

    }

    return pd.Series(metrics)
