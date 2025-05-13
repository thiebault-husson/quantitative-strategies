import numpy as np
import pandas as pd
import os

def align_returns(series1, series2, col1='strategy_returns', col2='benchmark_returns'):
    """
    Align two return series by index and return a DataFrame with two columns.
    Always save the result as a CSV in 'data/csv/aligned_strategy_vs_benchmark_returns.csv'.
    
    Args:
        series1 (pd.Series): First return series (e.g., strategy returns)
        series2 (pd.Series): Second return series (e.g., benchmark returns)
        col1 (str): Name for the first column (unused, kept for compatibility)
        col2 (str): Name for the second column (unused, kept for compatibility)

    Returns:
        pd.DataFrame: DataFrame with aligned returns, preserving original column names
    """
    aligned = pd.concat([series1, series2], axis=1)
    aligned = aligned.fillna(0)
    csv_path = 'data/csv/returns_strategy_vs_benchmark.csv'
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    aligned.to_csv(csv_path)
    return aligned

class PerformanceAnalytics:
    def __init__(self, returns_df: pd.DataFrame):
        """
        returns_df: DataFrame with columns ['strategy_returns', 'benchmark_returns']
        """
        self.returns_df = returns_df

    def _get_returns(self, which='strategy', period=None):
        r = self.returns_df[f'{which}_returns']
        if period is not None:
            r = r.iloc[-period:]
        return r

    def sharpe(self, which='strategy', risk_free_rate=0.0, period=None):
        """
        Calculate Sharpe ratio over the specified period (last N rows). If period is None, use all data.
        """
        r = self._get_returns(which, period)
        excess = r - risk_free_rate / 252
        return np.sqrt(252) * excess.mean() / excess.std() if excess.std() != 0 else 0

    def volatility(self, which='strategy', period=None):
        """
        Calculate annualized volatility over the specified period (last N rows). If period is None, use all data.
        """
        r = self._get_returns(which, period)
        return r.std() * np.sqrt(252)

    def drawdown(self, which='strategy', period=None):
        """
        Calculate max drawdown over the specified period (last N rows). If period is None, use all data.
        """
        r = self._get_returns(which, period)
        cum = (1 + r).cumprod()
        running_max = cum.cummax()
        drawdown = (cum / running_max) - 1
        return drawdown.min()

    def total_return(self, which='strategy', period=None):
        """
        Calculate total return over the specified period (last N rows). If period is None, use all data.
        """
        r = self._get_returns(which, period)
        return (1 + r).prod() - 1

    def annualized_return(self, which='strategy', period=None):
        """
        Calculate annualized return over the specified period (last N rows). If period is None, use all data.
        """
        r = self._get_returns(which, period)
        n_years = len(r) / 252
        total_ret = (1 + r).prod() - 1
        return (1 + total_ret) ** (1 / n_years) - 1 if n_years > 0 else np.nan

    # Add more methods as needed

# Usage:
# analytics = PerformanceAnalytics(aligned_df)
# print(analytics.sharpe('strategy'))
# print(analytics.sharpe('benchmark'))
