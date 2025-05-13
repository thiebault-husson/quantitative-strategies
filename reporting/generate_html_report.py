import os
import pandas as pd
from datetime import datetime
from reporting.graphs.graphs import (
    performance_gross_returns,
    performance_annualized_volatility,
    performance_sharpe_ratio,
    performance_max_drawdown,
    graph_base100,
    plot_portfolio_allocation,
    plot_cash_vs_invested
)
from reporting.graphs.tables import return_summary_table, annualized_return_per_year

def generate_html_report(
    aligned_returns: pd.DataFrame,
    results: dict = None,
    params: dict = None,
    data_summary: dict = None,
    position_sizes: pd.DataFrame = None
) -> None:
    """
    Generate an HTML report based on the first page of report_format_exemple.html.
    The HTML is saved in the performance_reports directory.
    """
    os.makedirs('reporting/performance_reports', exist_ok=True)
    html_path = 'reporting/performance_reports/strategy_performance_report.html'
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Prepare all tables
    gross_returns = performance_gross_returns(aligned_returns)
    vol_table = performance_annualized_volatility(aligned_returns)
    sharpe_table = performance_sharpe_ratio(aligned_returns)
    drawdown_table = performance_max_drawdown(aligned_returns)
    annual_return_table = annualized_return_per_year(aligned_returns)
    summary_table = return_summary_table(aligned_returns)

    # Format tables to display percentages with two decimal places
    annual_return_table = annual_return_table.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else x)
    summary_table = summary_table.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else x)
    vol_table = vol_table.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else x)
    drawdown_table = drawdown_table.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else x)

    # Format Sharpe Ratio table to display numbers with two decimal places
    sharpe_table = sharpe_table.applymap(lambda x: f'{x:.2f}' if pd.notnull(x) else x)

    # Generate the graph image
    graph_base100(aligned_returns, filename='reporting/performance_reports/base100_performance.png')
    # Plot the cash vs invested graph
    if position_sizes is not None:
        plot_cash_vs_invested(position_sizes, filename='strategy_portion_invested_overtime.png')

    # Extract parameters from the params dictionary
    strategy_tickers = params.get('strategy_tickers', [])
    start_date = params.get('start_date', 'N/A')
    end_date = params.get('end_date', 'N/A')
    yahoofinance_field = params.get('yahoofinance_field', ['N/A'])

    # Extract additional strategy parameters from the params dictionary
    lookback_period = params.get('lookback_period', 'N/A')
    volatility_lookback = params.get('volatility_lookback', 'N/A')
    risk_per_trade = params.get('risk_per_trade', 'N/A')
    max_position_size = params.get('max_position_size', 'N/A')

    # Add strategy summary information
    strategy_summary = {
        'Number of Tickers': len(strategy_tickers),
        'Start Date': start_date,
        'End Date': end_date,
        'Prices Used': ', '.join(yahoofinance_field),
        'Lookback Period': lookback_period,
        'Volatility Lookback': volatility_lookback,
        'Risk Per Trade': risk_per_trade,
        'Max Position Size': max_position_size
    }

    # Create a DataFrame for the strategy summary
    strategy_summary_table = pd.DataFrame(list(strategy_summary.items()), columns=['Parameter', 'Value'])

    # Create HTML content
    html_content = f"""
    <html>
    <head>
        <title>Strategy Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ text-align: center; }}
            .flex-container {{ display: flex; justify-content: space-between; margin: 20px 0; }}
            .flex-item {{ flex: 1; margin: 10px; }}
            .flex-item-table {{ flex: 0.5; margin: 10px; }}  /* Smaller flex for the table */
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            .grid-container {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }}
            .grid-item {{
                margin: 10px;
            }}
            .summary-container {{
                margin-bottom: 20px;
                width: 50%; /* Make the table narrower */
                text-align: left; /* Align the table to the left */
            }}
        </style>
    </head>
    <body>
        <h1>Strategy Performance Report</h1>
        <p style="text-align: center;">Generated: {today_str}</p>

        <div class="summary-container">
            <h2>Strategy Summary</h2>
            {strategy_summary_table.to_html(classes='table table-striped', index=False, border=0)}
        </div>
        <div class="summary-container">
            <!-- Blank container for additional content or spacing -->
        </div>

        <div class="flex-container">
            <div class="flex-item">
                <h2>Cumulative Performance (Base 100)</h2>
                <img src="base100_performance.png" alt="Cumulative Performance Graph" style="width: 100%;">
            </div>
            <div class="flex-item-table">
                <h2>Annualized Return Per Year</h2>
                {annual_return_table.to_html(classes='table table-striped', border=0)}
            </div>
        </div>

        <h2>Return Summary Table</h2>
        {summary_table.to_html(classes='table table-striped', border=0)}

        <div class="grid-container">
            <div class="grid-item">
                <h2>Annualized Volatility</h2>
                {vol_table.to_html(classes='table table-striped', border=0)}
            </div>
            <div class="grid-item">
                <h2>Sharpe Ratio</h2>
                {sharpe_table.to_html(classes='table table-striped', border=0)}
            </div>
            <div class="grid-item">
                <h2>Max Drawdown</h2>
                {drawdown_table.to_html(classes='table table-striped', border=0)}
            </div>
        </div>

        <footer style="text-align: right; font-size: 0.8em; color: gray;">
            Generated: {today_str}
        </footer>
    </body>
    </html>
    """

    # Save HTML content to file
    with open(html_path, 'w') as f:
        f.write(html_content)

