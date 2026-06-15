#!/usr/bin/env python3
"""
Apple Quality Scorecard - Financial Fundamentals Analysis
Calculates quality scores based on Apple's key financial metrics.
With Rich library for beautiful colored output.
"""

import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def score_metric(value, thresholds):
    """
    Score a metric on a 1-10 scale based on provided thresholds.
    Thresholds should be a dict with keys 1,2,3,...,10 mapping to values.
    """
    for score in range(10, 0, -1):
        if value >= thresholds.get(score, float('-inf')):
            return score
    return 1

def get_apple_financials():
    """
    Get Apple's financial data.
    Uses realistic current/recent Apple financial metrics (FY2024-2025).
    """
    print("Loading Apple financial data...")

    # Apple FY2024 actual results (ended Sept 28, 2024) + recent data
    # These are realistic figures based on Apple's latest earnings
    financials = {
        'ticker': 'AAPL',
        'company_name': 'Apple Inc.',
        'current_price': 235.50,  # Approximate current price
        'revenue': 391.035e9,      # FY2024: $391.035B
        'revenue_growth': 0.0206,  # ~2% YoY growth (FY2024 vs FY2023)
        'gross_margin': 0.4637,    # 46.37% (Q4 2024)
        'operating_margin': 0.3106,  # 31.06% (Q4 2024)
        'net_margin': 0.2432,      # 24.32% (Q4 2024)
        'total_debt': 106.308e9,   # ~$106.3B
        'cash': 37.149e9,          # ~$37.1B
        'free_cash_flow': 110.543e9,  # ~$110.5B (FY2024)
        'return_on_equity': 0.942,  # ~94.2% (TTM)
        'eps': 6.05,               # Approximate trailing EPS
    }

    return financials

def calculate_scores(financials):
    """Calculate individual metric scores (1-10 scale)."""

    # Define scoring thresholds for each metric
    # Higher values = higher scores (better fundamentals)

    # Revenue (in billions) - use trailing 12 months
    revenue_thresholds = {
        10: 400e9,    # $400B+
        9: 350e9,
        8: 300e9,
        7: 250e9,
        6: 200e9,
        5: 150e9,
        4: 100e9,
        3: 50e9,
        2: 20e9,
        1: 0
    }

    # Revenue Growth YoY - percentages
    revenue_growth_thresholds = {
        10: 0.25,     # 25%+ growth
        9: 0.20,
        8: 0.15,
        7: 0.10,
        6: 0.05,
        5: 0.02,      # 2% growth = break even
        4: 0.00,      # 0% growth = baseline
        3: -0.05,
        2: -0.10,
        1: -1.0       # Any decline
    }

    # Gross Margin - percentages (0.40 = 40%)
    margin_thresholds = {
        10: 0.50,     # 50%+
        9: 0.45,
        8: 0.40,
        7: 0.35,
        6: 0.30,
        5: 0.25,
        4: 0.20,
        3: 0.15,
        2: 0.10,
        1: 0
    }

    # Operating Margin
    op_margin_thresholds = {
        10: 0.35,     # 35%+
        9: 0.30,
        8: 0.25,
        7: 0.20,
        6: 0.15,
        5: 0.10,
        4: 0.08,
        3: 0.05,
        2: 0.02,
        1: 0
    }

    # Net Profit Margin
    net_margin_thresholds = {
        10: 0.30,     # 30%+
        9: 0.25,
        8: 0.20,
        7: 0.15,
        6: 0.10,
        5: 0.08,
        4: 0.06,
        3: 0.04,
        2: 0.02,
        1: 0
    }

    # Total Debt (lower is better) - in billions
    debt_thresholds = {
        10: 0,        # No debt (ideal)
        9: 10e9,
        8: 50e9,
        7: 100e9,
        6: 150e9,
        5: 200e9,     # High but manageable
        4: 250e9,
        3: 300e9,
        2: 350e9,
        1: 400e9
    }

    # Cash on Hand - in billions (higher is better)
    cash_thresholds = {
        10: 100e9,    # $100B+
        9: 80e9,
        8: 60e9,
        7: 40e9,
        6: 30e9,
        5: 20e9,
        4: 10e9,
        3: 5e9,
        2: 1e9,
        1: 0
    }

    # Free Cash Flow - in billions (higher is better)
    fcf_thresholds = {
        10: 100e9,    # $100B+
        9: 80e9,
        8: 60e9,
        7: 40e9,
        6: 30e9,
        5: 20e9,
        4: 10e9,
        3: 5e9,
        2: 1e9,
        1: 0
    }

    # Return on Equity - percentage (higher is better)
    roe_thresholds = {
        10: 1.00,     # 100%+
        9: 0.80,
        8: 0.60,
        7: 0.40,
        6: 0.25,
        5: 0.15,
        4: 0.10,
        3: 0.05,
        2: 0.02,
        1: 0
    }

    # Earnings Per Share - USD (higher is better)
    eps_thresholds = {
        10: 10.0,
        9: 8.0,
        8: 6.0,
        7: 4.5,
        6: 3.5,
        5: 2.5,
        4: 1.5,
        3: 1.0,
        2: 0.5,
        1: 0
    }

    # Calculate scores
    scores = {
        'Revenue': score_metric(financials['revenue'], revenue_thresholds),
        'Revenue Growth (YoY)': score_metric(financials['revenue_growth'], revenue_growth_thresholds),
        'Gross Margin': score_metric(financials['gross_margin'], margin_thresholds),
        'Operating Margin': score_metric(financials['operating_margin'], op_margin_thresholds),
        'Net Profit Margin': score_metric(financials['net_margin'], net_margin_thresholds),
        'Total Debt': score_metric(financials['total_debt'], debt_thresholds),
        'Cash on Hand': score_metric(financials['cash'], cash_thresholds),
        'Free Cash Flow': score_metric(financials['free_cash_flow'], fcf_thresholds),
        'Return on Equity': score_metric(financials['return_on_equity'], roe_thresholds),
        'Earnings Per Share': score_metric(financials['eps'], eps_thresholds),
    }

    return scores

def format_currency(value):
    """Format large numbers as billions/millions."""
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:.2f}"

def format_percentage(value):
    """Format decimal as percentage."""
    return f"{value*100:.2f}%"

def get_score_color(score):
    """Return color based on score value."""
    if score >= 9:
        return "bold bright_green"
    elif score >= 8:
        return "bold green"
    elif score >= 7:
        return "bold cyan"
    elif score >= 6:
        return "bold yellow"
    elif score >= 5:
        return "yellow"
    else:
        return "bold red"

def create_scorecard_table(financials, scores):
    """Create a beautiful Rich formatted scorecard table."""

    table = Table(title="[bold cyan]APPLE QUALITY SCORECARD[/bold cyan]",
                  show_header=True,
                  header_style="bold white on dark_blue",
                  border_style="cyan",
                  padding=(0, 1))

    table.add_column("Metric", style="bold white")
    table.add_column("Value", style="bright_white")
    table.add_column("Score", justify="center")

    metrics_data = [
        ('Revenue', format_currency(financials['revenue']), scores['Revenue']),
        ('Revenue Growth (YoY)', format_percentage(financials['revenue_growth']), scores['Revenue Growth (YoY)']),
        ('Gross Margin', format_percentage(financials['gross_margin']), scores['Gross Margin']),
        ('Operating Margin', format_percentage(financials['operating_margin']), scores['Operating Margin']),
        ('Net Profit Margin', format_percentage(financials['net_margin']), scores['Net Profit Margin']),
        ('Total Debt', format_currency(financials['total_debt']), scores['Total Debt']),
        ('Cash on Hand', format_currency(financials['cash']), scores['Cash on Hand']),
        ('Free Cash Flow', format_currency(financials['free_cash_flow']), scores['Free Cash Flow']),
        ('Return on Equity', format_percentage(financials['return_on_equity']), scores['Return on Equity']),
        ('Earnings Per Share', f"${financials['eps']:.2f}", scores['Earnings Per Share']),
    ]

    for metric, value, score in metrics_data:
        score_color = get_score_color(score)
        score_text = f"[{score_color}]{score}/10[/{score_color}]"
        table.add_row(metric, value, score_text)

    return table

def calculate_overall_score(scores):
    """Calculate overall quality score as average of all metric scores."""
    return sum(scores.values()) / len(scores)

def analyze_fundamentals(financials, scores, overall_score):
    """Provide detailed analysis of Apple's fundamentals with Rich formatting."""

    # Header
    title = Text("APPLE QUALITY SCORECARD ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Company info
    info_text = (f"[bold white]Company:[/bold white] [bright_cyan]{financials['company_name']}[/bright_cyan]  "
                f"[bold white]Ticker:[/bold white] [bright_yellow]{financials['ticker']}[/bright_yellow]  "
                f"[bold white]Price:[/bold white] [bright_green]${financials['current_price']:.2f}[/bright_green]  "
                f"[bold white]Date:[/bold white] [bright_white]{datetime.now().strftime('%Y-%m-%d')}[/bright_white]")
    console.print(info_text)
    console.print()

    # Scorecard table
    table = create_scorecard_table(financials, scores)
    console.print(table)
    console.print()

    # Overall Score Panel
    if overall_score >= 8.5:
        rating = "EXCELLENT"
        rating_color = "bold bright_green"
        score_color = "bold bright_green"
    elif overall_score >= 7.5:
        rating = "VERY GOOD"
        rating_color = "bold green"
        score_color = "bold green"
    elif overall_score >= 6.5:
        rating = "GOOD"
        rating_color = "bold cyan"
        score_color = "bold cyan"
    elif overall_score >= 5.5:
        rating = "FAIR"
        rating_color = "bold yellow"
        score_color = "bold yellow"
    else:
        rating = "POOR"
        rating_color = "bold red"
        score_color = "bold red"

    score_panel_text = f"[{score_color}]OVERALL QUALITY SCORE: {overall_score:.1f}/10[/{score_color}]\n[{rating_color}]Rating: {rating}[/{rating_color}]"
    score_panel = Panel(score_panel_text, border_style="cyan", style="on black")
    console.print(score_panel)
    console.print()

    # Strengths
    strengths = [(k, v) for k, v in scores.items() if v >= 8]
    strengths_text = "[bold bright_green]STRENGTHS (Score 8-10)[/bold bright_green]\n"
    if strengths:
        for metric, score in strengths:
            strengths_text += f"[bright_green]✓[/bright_green] {metric}: [bold green]{score}/10[/bold green]\n"
    else:
        strengths_text += "[dim](No metrics scored 8+)[/dim]"

    strengths_panel = Panel(strengths_text.strip(), border_style="green", style="on black")
    console.print(strengths_panel)
    console.print()

    # Weaknesses
    weaknesses = [(k, v) for k, v in scores.items() if v <= 4]
    weaknesses_text = "[bold bright_red]WEAKNESSES (Score 1-4)[/bold bright_red]\n"
    if weaknesses:
        for metric, score in weaknesses:
            weaknesses_text += f"[bright_red]✗[/bright_red] {metric}: [bold red]{score}/10[/bold red]\n"
    else:
        weaknesses_text += "[dim](No significant weaknesses)[/dim]"

    weaknesses_panel = Panel(weaknesses_text.strip(), border_style="red", style="on black")
    console.print(weaknesses_panel)
    console.print()

    # Detailed Analysis
    analysis_title = Text("DETAILED ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(analysis_title))
    console.print()

    # Revenue analysis
    if financials['revenue'] > 350e9:
        console.print(f"[bold bright_cyan]📊 REVENUE[/bold bright_cyan]\n"
                     f"With [bright_yellow]${financials['revenue']/1e9:.1f}B[/bright_yellow] in annual revenue, Apple is one of the largest "
                     f"technology companies globally. The massive revenue base provides strong financial stability.\n")

    # Growth analysis
    growth_rate = financials['revenue_growth']
    if growth_rate > 0.15:
        console.print(f"[bold bright_green]📈 GROWTH[/bold bright_green]\n"
                     f"Revenue growth of [bright_green]{growth_rate*100:.1f}%[/bright_green] indicates strong market demand and successful product launches.\n")
    elif growth_rate > 0.05:
        console.print(f"[bold cyan]📈 GROWTH[/bold cyan]\n"
                     f"Moderate revenue growth of [cyan]{growth_rate*100:.1f}%[/cyan] is typical for a mature company of Apple's size.\n")
    elif growth_rate > 0:
        console.print(f"[bold yellow]📈 GROWTH[/bold yellow]\n"
                     f"Slow revenue growth of [yellow]{growth_rate*100:.1f}%[/yellow] suggests market saturation challenges.\n")
    else:
        console.print(f"[bold bright_red]📉 GROWTH[/bold bright_red]\n"
                     f"Negative revenue growth of [bright_red]{growth_rate*100:.1f}%[/bright_red] indicates declining sales.\n")

    # Profitability analysis
    gm = financials['gross_margin']
    om = financials['operating_margin']
    nm = financials['net_margin']

    if gm > 0.40 and om > 0.25 and nm > 0.20:
        console.print(f"[bold bright_green]💰 PROFITABILITY[/bold bright_green]\n"
                     f"Exceptional margins across the board:\n"
                     f"  • Gross Margin: [bright_green]{gm*100:.1f}%[/bright_green] (Very high - excellent pricing power)\n"
                     f"  • Operating Margin: [bright_green]{om*100:.1f}%[/bright_green] (Excellent operational efficiency)\n"
                     f"  • Net Margin: [bright_green]{nm*100:.1f}%[/bright_green] (Superior bottom-line profitability)\n")
    elif gm > 0.35 and om > 0.20 and nm > 0.15:
        console.print(f"[bold green]💰 PROFITABILITY[/bold green]\n"
                     f"Strong margins indicating premium positioning:\n"
                     f"  • Gross Margin: [green]{gm*100:.1f}%[/green]\n"
                     f"  • Operating Margin: [green]{om*100:.1f}%[/green]\n"
                     f"  • Net Margin: [green]{nm*100:.1f}%[/green]\n")

    # Balance sheet analysis
    debt = financials['total_debt']
    cash = financials['cash']
    net_debt = debt - cash

    if net_debt < 0:
        console.print(f"[bold bright_cyan]🏦 BALANCE SHEET[/bold bright_cyan]\n"
                     f"Net cash position of [bright_green]${abs(net_debt)/1e9:.1f}B[/bright_green] indicates strong financial flexibility.\n"
                     f"  • Cash on Hand: [bright_yellow]${cash/1e9:.1f}B[/bright_yellow]\n"
                     f"  • Total Debt: [bright_yellow]${debt/1e9:.1f}B[/bright_yellow]\n")
    elif net_debt < 100e9:
        console.print(f"[bold cyan]🏦 BALANCE SHEET[/bold cyan]\n"
                     f"Conservative balance sheet with manageable debt.\n"
                     f"  • Net Debt: [yellow]${net_debt/1e9:.1f}B[/yellow]\n")
    else:
        console.print(f"[bold yellow]🏦 BALANCE SHEET[/bold yellow]\n"
                     f"Significant debt load of [yellow]${debt/1e9:.1f}B[/yellow], though offset by [bright_yellow]${cash/1e9:.1f}B[/bright_yellow] in cash.\n")

    # Cash flow analysis
    fcf = financials['free_cash_flow']
    if fcf > 80e9:
        console.print(f"[bold bright_green]💵 CASH FLOW[/bold bright_green]\n"
                     f"Exceptional free cash flow of [bright_green]${fcf/1e9:.1f}B[/bright_green] enables substantial dividends, buybacks, and R&D investments.\n")
    elif fcf > 40e9:
        console.print(f"[bold green]💵 CASH FLOW[/bold green]\n"
                     f"Strong free cash flow of [green]${fcf/1e9:.1f}B[/green] provides financial flexibility.\n")

    # Return on Equity analysis
    roe = financials['return_on_equity']
    if roe > 0.50:
        console.print(f"[bold bright_green]📈 EFFICIENCY[/bold bright_green]\n"
                     f"Exceptional ROE of [bright_green]{roe*100:.1f}%[/bright_green] demonstrates excellent capital allocation and shareholder value creation.\n")
    elif roe > 0.20:
        console.print(f"[bold green]📈 EFFICIENCY[/bold green]\n"
                     f"Strong ROE of [green]{roe*100:.1f}%[/green] shows effective capital deployment.\n")

    # Summary
    summary_title = Text("SUMMARY", style="bold bright_cyan")
    console.print(Align.center(summary_title))
    console.print()

    if overall_score >= 8.0:
        summary_text = ("[bold bright_green]Apple demonstrates exceptional financial fundamentals with:[/bold bright_green]\n"
                       "[bright_green]•[/bright_green] Market-leading profitability and margins\n"
                       "[bright_green]•[/bright_green] Strong cash generation and balance sheet strength\n"
                       "[bright_green]•[/bright_green] Efficient capital allocation (high ROE)\n"
                       "[bright_green]•[/bright_green] Premium brand positioning justifying high gross margins\n\n"
                       "[bright_cyan]This company represents one of the highest-quality businesses in technology.[/bright_cyan]")
    elif overall_score >= 7.0:
        summary_text = ("[bold green]Apple shows very good financial fundamentals with strengths in:[/bold green]\n"
                       "[green]•[/green] Profitability and operational efficiency\n"
                       "[green]•[/green] Cash generation capabilities\n"
                       "[green]•[/green] Financial stability\n\n"
                       "[cyan]Apple remains a high-quality investment with solid business metrics.[/cyan]")
    else:
        summary_text = "[yellow]Apple's fundamentals suggest some areas of concern that warrant attention.[/yellow]"

    summary_panel = Panel(summary_text, border_style="cyan", style="on black")
    console.print(summary_panel)

def main():
    """Main execution function."""
    try:
        # Fetch financials
        financials = get_apple_financials()

        # Calculate scores
        scores = calculate_scores(financials)

        # Calculate overall score
        overall_score = calculate_overall_score(scores)

        # Display analysis
        analyze_fundamentals(financials, scores, overall_score)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich pandas[/cyan]")

if __name__ == "__main__":
    main()
