import pandas as pd
import numpy as np
from .base import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, lookback_period, volatility_lookback, risk_per_trade, max_position_size):
        self.lookback_period = lookback_period
        self.volatility_lookback = volatility_lookback
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size

    def generate_signals(self, prices: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=prices.index, columns=prices.columns)
        for ticker in prices.columns:
            ma = prices[ticker].rolling(window=self.lookback_period).mean()
            signals[ticker] = np.where(prices[ticker] > ma, 1, 0)
        return signals

    def size_positions(self, prices: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
        position_sizes = pd.DataFrame(index=prices.index, columns=prices.columns)
        for ticker in prices.columns:
            returns = prices[ticker].pct_change()
            volatility = returns.rolling(window=self.volatility_lookback).std()
            position_sizes[ticker] = self.risk_per_trade / volatility
            position_sizes[ticker] = position_sizes[ticker].clip(0, self.max_position_size)
        return position_sizes * signals

    def calculate_returns(self, prices: pd.DataFrame, signals: pd.DataFrame, position_sizes: pd.DataFrame) -> pd.Series:
        returns = prices.pct_change()
        strategy_returns = returns * signals.shift(1) * position_sizes.shift(1)
        portfolio_returns = strategy_returns.sum(axis=1)
        return portfolio_returns