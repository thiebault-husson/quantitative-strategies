import pandas as pd
import numpy as np
from reporting.performance_metrics.calculate_performance_metrics import PerformanceAnalytics

def return_summary_table(df):
    """
    Compute a matrix of returns for each column in df over various periods.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns)
    Returns:
        pd.DataFrame: Table with rows as column names of df and columns for total and annualized returns
    """
    periods = {
        '1 Mo': 21,
        '3 Mo': 63,
        '1 Yr': 252,
        'YTD': None,
        '3 Yr (Ann)': 756,
        '5 Yr (Ann)': 1260,
        '10 Yr (Ann)': 2520,
        'Since Start (Ann)': None
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
                if len(ytd_returns) > 0:
                    row[period] = analytics.total_return(which=col, period=len(ytd_returns)) * 100
                else:
                    row[period] = np.nan
            elif period == 'Since Start':
                row[f'Since {start_date_str}'] = analytics.annualized_return(which=col) * 100 if len(df) > 252 else analytics.total_return(which=col) * 100
            elif days is not None:
                if len(df) >= days:
                    if days < 252:
                        row[period] = analytics.total_return(which=col, period=days) * 100
                    else:
                        row[period] = analytics.annualized_return(which=col, period=days) * 100
                else:
                    row[period] = np.nan
        results.append(row)
    result_df = pd.DataFrame(results, index=df.columns)
    cols = [c for c in result_df.columns if not c.startswith('Since ')]
    since_col = [c for c in result_df.columns if c.startswith('Since ')]
    result_df = result_df[cols + since_col]
    return result_df


def annualized_return_per_year(df):
    """
    Compute the annualized return for each year of available data in the DataFrame for each column.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns) and a date index
    Returns:
        pd.DataFrame: DataFrame with each year as a row and the annualized return for each column
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex")

    annual_returns_df = pd.DataFrame()
    for col in df.columns:
        col_annual_returns = {}
        for year in df.index.year.unique():
            year_data = df[df.index.year == year]
            if len(year_data) >= 200:  # Only consider years with at least 200 data points
                analytics = PerformanceAnalytics(pd.DataFrame({f'{col}_returns': year_data[col]}))
                annualized_return = analytics.annualized_return(which=col) * 100
                col_annual_returns[year] = annualized_return
        col_df = pd.DataFrame.from_dict(col_annual_returns, orient='index', columns=[col])
        annual_returns_df = pd.concat([annual_returns_df, col_df], axis=1)
    return annual_returns_df




