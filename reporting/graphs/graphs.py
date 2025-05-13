import matplotlib.pyplot as plt
import pandas as pd
from reporting.performance_metrics.calculate_performance_metrics import PerformanceAnalytics
import numpy as np

def plot_portfolio_value(portfolio_values, filename='portfolio_value.png'):
    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_values, label='Portfolio Value')
    plt.title('Portfolio Value Over Time')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def performance_gross_returns(df):
    """
    Compute a table of gross returns for each column in df over various periods.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns)
    Returns:
        pd.DataFrame: Table with columns ['1 Mo', '3 Mo', '1 Yr', 'YTD', '3 Yr', '5 Yr', '10 Yr', 'Since <start_date>']
        (all values in percent)
    """
    periods = {
        '1 Mo': 21,
        '3 Mo': 63,
        '1 Yr (Ann)': 252,
        'YTD': None, 
        '3 Yr (Ann)': 756,
        '5 Yr (Ann)': 1260,
        '10 Yr (Ann)': 2520,
        'Since Start': None
    }
    results = []
    # Get the earliest date in the DataFrame
    if isinstance(df.index, pd.DatetimeIndex):
        start_date_str = df.index.min().strftime('%Y-%m-%d')
    else:
        start_date_str = str(df.index[0])
    for col in df.columns:
        analytics = PerformanceAnalytics(pd.DataFrame({f'{col}_returns': df[col]}))
        row = {}
        for period, days in periods.items():
            if period == 'YTD':
                idx = df.index
                last_date = idx[-1]
                ytd_start = pd.Timestamp(year=last_date.year, month=1, day=1)
                ytd_mask = idx >= ytd_start
                ytd_returns = df[col][ytd_mask]
                if len(ytd_returns) > 0:
                    row[period] = analytics.total_return(which=col, period=len(ytd_returns))
                else:
                    row[period] = np.nan
            elif period == 'Since Start':
                row[f'Since {start_date_str}'] = analytics.annualized_return(which=col) if len(df) > 252 else analytics.total_return(which=col)
            elif days is not None:
                if len(df) >= days:
                    if days < 252:
                        row[period] = analytics.total_return(which=col, period=days)
                    else:
                        row[period] = analytics.annualized_return(which=col, period=days)
                else:
                    row[period] = np.nan
        results.append(row)
    # Remove the old 'Since Start' column if present
    result_df = pd.DataFrame(results, index=df.columns)
    # Reorder columns to put 'Since <start_date>' last
    cols = [c for c in result_df.columns if not c.startswith('Since ')]
    since_col = [c for c in result_df.columns if c.startswith('Since ')]
    result_df = result_df[cols + since_col]
    return result_df * 100  # Convert to percent

def performance_annualized_volatility(df):
    """
    Compute a table of annualized volatility for each column in df over various periods.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns)
    Returns:
        pd.DataFrame: Table with columns ['1 Mo', '3 Mo', '1 Yr', 'YTD', '3 Yr', '5 Yr', '10 Yr', 'Since <start_date>']
        (all values in percent)
    """
    periods = {
        '1 Yr (Ann)': 252,
        '3 Yr (Ann)': 756,
        '5 Yr (Ann)': 1260,
        '10 Yr (Ann)': 2520,
        'Since Start': None
    }
    results = []
    # Get the earliest date in the DataFrame
    if isinstance(df.index, pd.DatetimeIndex):
        start_date_str = df.index.min().strftime('%Y-%m-%d')
    else:
        start_date_str = str(df.index[0])
    for col in df.columns:
        analytics = PerformanceAnalytics(pd.DataFrame({f'{col}_returns': df[col]}))
        row = {}
        for period, days in periods.items():
            if period == 'YTD':
                idx = df.index
                last_date = idx[-1]
                ytd_start = pd.Timestamp(year=last_date.year, month=1, day=1)
                ytd_mask = idx >= ytd_start
                ytd_returns = df[col][ytd_mask]
                if len(ytd_returns) > 1:
                    row[period] = analytics.volatility(which=col, period=len(ytd_returns))
                else:
                    row[period] = np.nan
            elif period == 'Since Start':
                row[f'Since {start_date_str}'] = analytics.volatility(which=col)
            elif days is not None:
                if len(df) >= days:
                    row[period] = analytics.volatility(which=col, period=days)
                else:
                    row[period] = np.nan
        results.append(row)
    result_df = pd.DataFrame(results, index=df.columns)
    cols = [c for c in result_df.columns if not c.startswith('Since ')]
    since_col = [c for c in result_df.columns if c.startswith('Since ')]
    result_df = result_df[cols + since_col]
    return result_df * 100  # Convert to percent

def performance_sharpe_ratio(df):
    """
    Compute a table of annualized Sharpe ratio for each column in df over various periods.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns)
    Returns:
        pd.DataFrame: Table with columns ['1 Yr (Ann)', '3 Yr (Ann)', '5 Yr (Ann)', '10 Yr (Ann)', 'Since <start_date>']
    """
    periods = {
        '1 Yr (Ann)': 252,
        '3 Yr (Ann)': 756,
        '5 Yr (Ann)': 1260,
        '10 Yr (Ann)': 2520,
        'Since Start': None
    }
    results = []
    if isinstance(df.index, pd.DatetimeIndex):
        start_date_str = df.index.min().strftime('%Y-%m-%d')
    else:
        start_date_str = str(df.index[0])
    for col in df.columns:
        analytics = PerformanceAnalytics(pd.DataFrame({f'{col}_returns': df[col]}))
        row = {}
        for period, days in periods.items():
            if period == 'YTD':
                idx = df.index
                last_date = idx[-1]
                ytd_start = pd.Timestamp(year=last_date.year, month=1, day=1)
                ytd_mask = idx >= ytd_start
                ytd_returns = df[col][ytd_mask]
                if len(ytd_returns) > 1:
                    row[period] = analytics.sharpe(which=col, period=len(ytd_returns))
                else:
                    row[period] = np.nan
            elif period == 'Since Start':
                row[f'Since {start_date_str}'] = analytics.sharpe(which=col)
            elif days is not None:
                if len(df) >= days:
                    row[period] = analytics.sharpe(which=col, period=days)
                else:
                    row[period] = np.nan
        results.append(row)
    result_df = pd.DataFrame(results, index=df.columns)
    cols = [c for c in result_df.columns if not c.startswith('Since ')]
    since_col = [c for c in result_df.columns if c.startswith('Since ')]
    result_df = result_df[cols + since_col]
    return result_df

def performance_max_drawdown(df):
    """
    Compute a table of max drawdown for each column in df over various periods.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns)
    Returns:
        pd.DataFrame: Table with columns ['1 Yr (Ann)', '3 Yr (Ann)', '5 Yr (Ann)', '10 Yr (Ann)', 'Since <start_date>']
        (all values in percent)
    """
    periods = {
        '1 Yr (Ann)': 252,
        '3 Yr (Ann)': 756,
        '5 Yr (Ann)': 1260,
        '10 Yr (Ann)': 2520,
        'Since Start': None
    }
    results = []
    if isinstance(df.index, pd.DatetimeIndex):
        start_date_str = df.index.min().strftime('%Y-%m-%d')
    else:
        start_date_str = str(df.index[0])
    for col in df.columns:
        analytics = PerformanceAnalytics(pd.DataFrame({f'{col}_returns': df[col]}))
        row = {}
        for period, days in periods.items():
            if period == 'YTD':
                idx = df.index
                last_date = idx[-1]
                ytd_start = pd.Timestamp(year=last_date.year, month=1, day=1)
                ytd_mask = idx >= ytd_start
                ytd_returns = df[col][ytd_mask]
                if len(ytd_returns) > 1:
                    row[period] = analytics.drawdown(which=col, period=len(ytd_returns))
                else:
                    row[period] = np.nan
            elif period == 'Since Start':
                row[f'Since {start_date_str}'] = analytics.drawdown(which=col)
            elif days is not None:
                if len(df) >= days:
                    row[period] = analytics.drawdown(which=col, period=days)
                else:
                    row[period] = np.nan
        results.append(row)
    result_df = pd.DataFrame(results, index=df.columns)
    cols = [c for c in result_df.columns if not c.startswith('Since ')]
    since_col = [c for c in result_df.columns if c.startswith('Since ')]
    result_df = result_df[cols + since_col]
    return result_df * 100  # Convert to percent

def graph_base100(df, filename='base100_performance.png'):
    """
    Plot cumulative performance (base 100) for each column in a DataFrame of returns.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns) and a date index
        filename (str): File name to save the plot
    """
    base100 = (1 + df).cumprod() * 100
    plt.figure(figsize=(12, 6))
    for col in base100.columns:
        plt.plot(base100.index, base100[col], label=col)
    plt.title('Cumulative Performance (Base 100)')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Performance (Base 100)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


