import pandas as pd
from strategies.trend_following import TrendFollowingStrategy
from backtest.engine import BacktestEngine
from reporting.performance_metrics.calculate_performance_metrics import align_returns
from data.index_components import get_sp500_tickers
import numpy as np
from data.historical_data import get_historical_data
from reporting.graphs.graphs import performance_gross_returns, performance_annualized_volatility, performance_sharpe_ratio, performance_max_drawdown
from reporting.generate_html_report import generate_html_report

# Get tickers to be used in strategy
strategy_tickers = get_sp500_tickers()
# Define benchmark ticker, ^GSPC for SP500
benchmark_ticker = '^GSPC'

# Load history of price data
start_date = '2014-01-01'
end_date = '2025-05-12'
yahoofinance_field = ['Open']

strategy_components_price_data = get_historical_data(strategy_tickers, start_date, end_date, fields=yahoofinance_field)
benchmark_price_data = get_historical_data([benchmark_ticker], start_date, end_date, fields=yahoofinance_field)

# Instantiate your strategy
lookback_period = 200
volatility_lookback=20
risk_per_trade=0.01
max_position_size=0.05

strategy = TrendFollowingStrategy(
    lookback_period=lookback_period,
    volatility_lookback=volatility_lookback,
    risk_per_trade=risk_per_trade,
    max_position_size=max_position_size
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

# Pass additional parameters to generate_html_report
params = {
    'strategy_tickers': strategy_tickers,
    'start_date': start_date,
    'end_date': end_date,
    'yahoofinance_field': yahoofinance_field,
    'lookback_period': lookback_period,
    'volatility_lookback': volatility_lookback,
    'risk_per_trade': risk_per_trade,
    'max_position_size': max_position_size
}

# Pass position_sizes to generate_html_report
generate_html_report(aligned_returns_trimmed, params=params, position_sizes=results['position_sizes'])
