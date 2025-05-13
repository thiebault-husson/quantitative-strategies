import pandas as pd
from reporting.graphs.graphs import (
    plot_portfolio_value,
    graph_base100,
    performance_gross_returns,
    performance_annualized_volatility,
    performance_sharpe_ratio,
    performance_max_drawdown
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
from datetime import datetime
import matplotlib.gridspec as gridspec


def generate_strategy_report(
    aligned_returns: pd.DataFrame,
    results: dict = None,
    params: dict = None,
    data_summary: dict = None
) -> None:
    """
    Generate a single-page A4 PDF report: title, graph, and all tables stacked vertically with section headers.
    The PDF is saved in the performance_reports directory.
    """
    os.makedirs('reporting/performance_reports', exist_ok=True)
    pdf_path = 'reporting/performance_reports/strategy_performance_report.pdf'
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Prepare all tables
    gross_returns = performance_gross_returns(aligned_returns)
    vol_table = performance_annualized_volatility(aligned_returns)
    sharpe_table = performance_sharpe_ratio(aligned_returns)
    drawdown_table = performance_max_drawdown(aligned_returns)

    # Layout: title, graph, 4 tables, footer
    n_sections = 8
    height_ratios = [0.5, 3.0, 0.2, 1.8, 1.2, 1.2, 1.2, 0.2]

    fig = plt.figure(figsize=(8.27, 11.69))
    gs = gridspec.GridSpec(n_sections, 1, height_ratios=height_ratios, hspace=0.6, figure=fig)

    # Title
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis('off')
    ax_title.text(0.5, 0.7, "Strategy Performance Report", fontsize=20, fontweight='bold', ha='center')
    ax_title.text(0.5, 0.3, f"Generated: {today_str}", fontsize=10, ha='center', color='gray')

    # Graph
    ax_graph = fig.add_subplot(gs[1])
    base100 = (1 + aligned_returns).cumprod() * 100
    for col in base100.columns:
        ax_graph.plot(base100.index, base100[col], label=col, linewidth=2)
    ax_graph.set_title('Cumulative Performance (Base 100)', fontsize=12, fontweight='bold')
    ax_graph.set_xlabel('Date', fontsize=10)
    ax_graph.set_ylabel('Cumulative Performance (Base 100)', fontsize=10)
    ax_graph.legend(fontsize=8)
    ax_graph.grid(True, linestyle='--', alpha=0.6)

    # Helper for pretty tables
    def pretty_table(ax, table_df, title):
        ax.axis('off')
        ax.set_title(title, fontsize=11, fontweight='bold', pad=8)
        tbl = ax.table(
            cellText=table_df.round(2).values,
            colLabels=table_df.columns,
            rowLabels=table_df.index,
            loc='center',
            cellLoc='center',
            colLoc='center',
            edges='open',
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.scale(1.05, 1.1)
        for (r, c), cell in tbl.get_celld().items():
            if r == 0 or c == -1:
                cell.set_fontsize(9)
                cell.set_text_props(weight='bold')
            if r == 0:
                cell.set_facecolor('#f2f2f2')
        return ax

    # Tables
    table_grid_indices = [3, 4, 5, 6]  # Skip 2 (spacer)
    for i, (table, title) in enumerate([
        (gross_returns, "Gross Returns"),
        (vol_table, "Annualized Volatility"),
        (sharpe_table, "Sharpe Ratio"),
        (drawdown_table, "Max Drawdown")
    ]):
        ax_tbl = fig.add_subplot(gs[table_grid_indices[i]])
        pretty_table(ax_tbl, table, title)

    # Footer
    fig.text(0.99, 0.01, f"Generated: {today_str}", ha='right', va='bottom', fontsize=8, color='gray')
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.close(fig)
    print(f"Strategy performance PDF report saved to {pdf_path}")

