import pandas as pd
from strategies.trend_following import TrendFollowingStrategy
from backtest.engine import BacktestEngine
from reporting.generate_report import generate_strategy_report
from reporting.performance_metrics.calculate_performance_metrics import align_returns
from data.index_components import get_sp500_tickers
import numpy as np
from data.historical_data import get_historical_data
from reporting.graphs.graphs import performance_gross_returns, performance_annualized_volatility, performance_sharpe_ratio, performance_max_drawdown

# Get tickers to be used in strategy
strategy_tickers = get_sp500_tickers()
# Define benchmark ticker, ^GSPC for SP500
benchmark_ticker = '^GSPC'

# Load history of price data
start_date = '2014-01-01'
end_date = '2025-05-12'
yahoofinance_field = ['Open']

strategy_components_price_data = get_historical_data(strategy_tickers[:10], start_date, end_date, fields=yahoofinance_field)
benchmark_price_data = get_historical_data([benchmark_ticker], start_date, end_date, fields=yahoofinance_field)

# Instantiate your strategy
lookback_period = 200

strategy = TrendFollowingStrategy(
    lookback_period=lookback_period,
    volatility_lookback=20,
    risk_per_trade=0.01,
    max_position_size=0.05
)

# Run the backtest
engine = BacktestEngine(strategy, strategy_components_price_data, initial_cash=100000.0)
results = engine.run()

#Run analytics
strategy_returns = results['returns']
strategy_returns.name = "Trend Following Strategy"
benchmark_returns = benchmark_price_data[benchmark_price_data.columns[0]].pct_change()

#Match historical returns ti date index
aligned_returns = align_returns(strategy_returns, benchmark_returns)
aligned_returns_trimmed = aligned_returns.iloc[lookback_period:]

generate_strategy_report(aligned_returns_trimmed)
