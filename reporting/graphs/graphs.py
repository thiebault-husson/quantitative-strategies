import matplotlib.pyplot as plt
import pandas as pd
from reporting.performance_metrics.calculate_performance_metrics import PerformanceAnalytics
import numpy as np
import os

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

def calculate_performance_metric(df, metric_function):
    """
    General function to compute a performance metric for each column in df over various periods.
    Args:
        df (pd.DataFrame): DataFrame with columns as return series (daily returns)
        metric_function (callable): Function to calculate the desired metric
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
                    row[period] = metric_function(analytics, which=col, period=len(ytd_returns))
                else:
                    row[period] = np.nan
            elif period == 'Since Start':
                row[f'Since {start_date_str}'] = metric_function(analytics, which=col)
            elif days is not None:
                if len(df) >= days:
                    row[period] = metric_function(analytics, which=col, period=days)
                else:
                    row[period] = np.nan
        results.append(row)
    result_df = pd.DataFrame(results, index=df.columns)
    cols = [c for c in result_df.columns if not c.startswith('Since ')]
    since_col = [c for c in result_df.columns if c.startswith('Since ')]
    result_df = result_df[cols + since_col]
    return result_df

def performance_gross_returns(df):
    return calculate_performance_metric(df, lambda analytics, **kwargs: analytics.total_return(**kwargs) * 100)

def performance_annualized_volatility(df):
    return calculate_performance_metric(df, lambda analytics, **kwargs: analytics.volatility(**kwargs) * 100)

def performance_sharpe_ratio(df):
    return calculate_performance_metric(df, lambda analytics, **kwargs: analytics.sharpe(**kwargs))

def performance_max_drawdown(df):
    return calculate_performance_metric(df, lambda analytics, **kwargs: analytics.drawdown(**kwargs) * 100)

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

def plot_portfolio_allocation(position_sizes, filename='strategy_allocation_overtime.png'):
    """
    Plot a stacked area chart showing the portfolio allocation over time.
    
    Args:
        position_sizes (pd.DataFrame): DataFrame with columns representing different positions.
        filename (str): File name to save the plot.
    """
    # Ensure the directory exists
    os.makedirs('reporting/performance_reports', exist_ok=True)
    
    # Calculate the percentage allocation for each position
    percentage_allocation = position_sizes.copy()
    
    # Calculate cash as 1 minus the sum of position sizes
    percentage_allocation['Cash'] = 1 - position_sizes.sum(axis=1)
    
    # Convert to percentage
    percentage_allocation *= 100
    
    # Plot the stacked area chart
    plt.figure(figsize=(12, 6))
    plt.stackplot(percentage_allocation.index, percentage_allocation.T, labels=percentage_allocation.columns)
    plt.title('Portfolio Allocation Over Time')
    plt.xlabel('Date')
    plt.ylabel('Percentage of Portfolio (%)')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join('reporting/performance_reports', filename))
    plt.close()

def plot_cash_vs_invested(position_sizes, filename='strategy_portion_invested_overtime.png'):
    """
    Plot a stacked area chart showing the percentage of cash vs invested over time.
    
    Args:
        position_sizes (pd.DataFrame): DataFrame with columns representing different positions.
        filename (str): File name to save the plot.
    """
    # Ensure the directory exists
    os.makedirs('reporting/performance_reports', exist_ok=True)
    
    # Calculate the percentage of invested
    invested_percentage = position_sizes.sum(axis=1)
    
    # Calculate cash as 1 minus the invested percentage
    cash_percentage = 1 - invested_percentage
    
    # Create a DataFrame for plotting
    data = pd.DataFrame({'Invested': invested_percentage, 'Cash': cash_percentage}) * 100
    
    # Plot the stacked area chart
    plt.figure(figsize=(12, 6))
    plt.stackplot(data.index, data.T, labels=data.columns)
    plt.title('Cash vs Invested Over Time')
    plt.xlabel('Date')
    plt.ylabel('Percentage of Portfolio (%)')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join('reporting/performance_reports', filename))
    plt.close()



