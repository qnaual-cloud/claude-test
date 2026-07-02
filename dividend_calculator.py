#!/usr/bin/env python3
"""
Dividend Income Calculator
Calculate portfolio dividend income with current dividend rates.
Displays results in a visually striking format for presentations.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def get_portfolio_holdings():
    """Get portfolio holdings with dividend data."""
    print("Loading portfolio dividend data...\n")

    # Portfolio holdings with current dividend information (as of 2024-2025)
    holdings = [
        {
            'ticker': 'TSLA',
            'company': 'Tesla Inc.',
            'shares': 10,
            'current_price': 238.45,
            'annual_dividend_per_share': 0.00,  # Tesla doesn't pay dividends
            'dividend_yield': 0.0000,
            'ex_dividend_date': 'N/A',
            'payment_frequency': 'None',
        },
        {
            'ticker': 'AAPL',
            'company': 'Apple Inc.',
            'shares': 5,
            'current_price': 235.50,
            'annual_dividend_per_share': 1.00,  # ~$0.25 quarterly
            'dividend_yield': 0.0042,  # ~0.42%
            'ex_dividend_date': 'May 2025',
            'payment_frequency': 'Quarterly',
        },
        {
            'ticker': 'NVDA',
            'company': 'NVIDIA Corporation',
            'shares': 8,
            'current_price': 875.00,
            'annual_dividend_per_share': 0.16,  # ~$0.04 quarterly (recently started)
            'dividend_yield': 0.0002,  # ~0.02%
            'ex_dividend_date': 'June 2025',
            'payment_frequency': 'Quarterly',
        },
    ]

    return holdings

def calculate_dividend_metrics(holdings):
    """Calculate dividend metrics for each holding."""
    for holding in holdings:
        # Current position value
        holding['position_value'] = holding['shares'] * holding['current_price']

        # Annual dividend income from this position
        holding['annual_dividend_income'] = holding['shares'] * holding['annual_dividend_per_share']

        # Quarterly dividend income
        holding['quarterly_dividend_income'] = holding['annual_dividend_income'] / 4

        # Monthly dividend income
        holding['monthly_dividend_income'] = holding['annual_dividend_income'] / 12

        # Calculate yield (price-based)
        if holding['current_price'] > 0:
            holding['yield_pct'] = (holding['annual_dividend_per_share'] / holding['current_price']) * 100
        else:
            holding['yield_pct'] = 0

    return holdings

def calculate_portfolio_totals(holdings):
    """Calculate portfolio-level dividend metrics."""
    totals = {
        'total_position_value': sum(h['position_value'] for h in holdings),
        'total_annual_dividend': sum(h['annual_dividend_income'] for h in holdings),
        'total_quarterly_dividend': sum(h['quarterly_dividend_income'] for h in holdings),
        'total_monthly_dividend': sum(h['monthly_dividend_income'] for h in holdings),
        'total_daily_dividend': sum(h['monthly_dividend_income'] for h in holdings) / 30.4,
        'dividend_paying_stocks': sum(1 for h in holdings if h['annual_dividend_per_share'] > 0),
        'total_stocks': len(holdings),
    }

    # Portfolio dividend yield
    if totals['total_position_value'] > 0:
        totals['portfolio_yield_pct'] = (totals['total_annual_dividend'] / totals['total_position_value']) * 100
    else:
        totals['portfolio_yield_pct'] = 0

    return totals

def display_dividend_analysis(holdings, totals):
    """Display dividend income analysis with rich formatting."""

    # Header
    title = Text("PORTFOLIO DIVIDEND INCOME CALCULATOR", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Analysis date
    date_text = f"[dim]Analysis Date: {datetime.now().strftime('%B %d, %Y')}[/dim]"
    console.print(Align.center(date_text))
    console.print()

    # Key Metrics Summary Panel
    summary_text = (
        f"[bold white]Total Portfolio Value:[/bold white] [bright_cyan]${totals['total_position_value']:,.2f}[/bright_cyan]\n"
        f"[bold white]Annual Dividend Income:[/bold white] [bright_green]${totals['total_annual_dividend']:.2f}[/bright_green]\n"
        f"[bold white]Portfolio Dividend Yield:[/bold white] [bright_green]{totals['portfolio_yield_pct']:.3f}%[/bright_green]\n"
        f"[bold white]Dividend-Paying Stocks:[/bold white] [bright_yellow]{totals['dividend_paying_stocks']}/{totals['total_stocks']}[/bright_yellow]"
    )
    summary_panel = Panel(summary_text, border_style="bright_green", style="on black",
                         title="[bold bright_green]KEY DIVIDEND METRICS[/bold bright_green]")
    console.print(summary_panel)
    console.print()

    # Main Holdings Table
    table = Table(title="[bold bright_cyan]YOUR DIVIDEND-EARNING PORTFOLIO[/bold bright_cyan]",
                  show_header=True,
                  header_style="bold white on dark_green",
                  border_style="bright_green",
                  padding=(0, 1))

    table.add_column("Ticker", style="bold bright_yellow", justify="center")
    table.add_column("Company", style="bold white")
    table.add_column("Shares", style="bright_cyan", justify="center")
    table.add_column("Price", style="bright_cyan", justify="right")
    table.add_column("Position Value", style="bright_cyan", justify="right")
    table.add_column("Div/Share", style="bright_green", justify="right")
    table.add_column("Annual Income", style="bold bright_green", justify="right")
    table.add_column("Yield %", style="bright_yellow", justify="center")

    for holding in holdings:
        # Color code based on dividend status
        if holding['annual_dividend_per_share'] > 0:
            ticker_style = "bold bright_green"
            company_style = "green"
            div_income_style = "bold bright_green"
        else:
            ticker_style = "dim white"
            company_style = "dim white"
            div_income_style = "dim yellow"

        table.add_row(
            f"[{ticker_style}]{holding['ticker']}[/{ticker_style}]",
            f"[{company_style}]{holding['company']}[/{company_style}]",
            str(holding['shares']),
            f"${holding['current_price']:.2f}",
            f"${holding['position_value']:,.2f}",
            f"${holding['annual_dividend_per_share']:.2f}",
            f"[{div_income_style}]${holding['annual_dividend_income']:.2f}[/{div_income_style}]",
            f"{holding['yield_pct']:.3f}%"
        )

    console.print(table)
    console.print()

    # Dividend Income Breakdown - Annual
    console.print("[bold bright_green]💰 ANNUAL DIVIDEND INCOME BREAKDOWN[/bold bright_green]\n")

    for holding in holdings:
        if holding['annual_dividend_per_share'] > 0:
            console.print(f"[bold green]{holding['ticker']}[/bold green] ({holding['company']})")
            console.print(f"  [green]●[/green] {holding['shares']} shares × ${holding['annual_dividend_per_share']:.2f}/share = [bold bright_green]${holding['annual_dividend_income']:.2f}/year[/bold bright_green]")
        else:
            console.print(f"[dim]{holding['ticker']}[/dim] ({holding['company']})")
            console.print(f"  [dim]●[/dim] [dim]No dividend - Growth stock[/dim]")
        console.print()

    # Income Frequency Table
    frequency_table = Table(title="[bold bright_cyan]DIVIDEND PAYMENT FREQUENCY[/bold bright_cyan]",
                           show_header=True,
                           header_style="bold white on dark_green",
                           border_style="bright_green",
                           padding=(0, 1))

    frequency_table.add_column("Period", style="bold white")
    frequency_table.add_column("Annual", style="bright_green", justify="right")
    frequency_table.add_column("Per Payment", style="bright_cyan", justify="right")
    frequency_table.add_column("Description", style="white")

    # Annual
    frequency_table.add_row(
        "[bold bright_green]Annual[/bold bright_green]",
        f"[bold bright_green]${totals['total_annual_dividend']:.2f}[/bold bright_green]",
        "[bright_green]1x per year[/bright_green]",
        "Total yearly dividend income"
    )

    # Quarterly
    frequency_table.add_row(
        "[bold cyan]Quarterly[/bold cyan]",
        f"[cyan]${totals['total_quarterly_dividend']:.2f}[/cyan]",
        "[bright_cyan]${:.2f}[/bright_cyan]".format(totals['total_quarterly_dividend']),
        "Every 3 months"
    )

    # Monthly
    frequency_table.add_row(
        "[bold yellow]Monthly Average[/bold yellow]",
        f"[yellow]${totals['total_monthly_dividend']:.2f}[/yellow]",
        f"[bright_yellow]${totals['total_monthly_dividend']:.2f}[/bright_yellow]",
        "Approximate monthly income"
    )

    # Daily
    frequency_table.add_row(
        "[bold bright_black]Daily Average[/bold bright_black]",
        f"[bright_black]${totals['total_daily_dividend']:.2f}[/bright_black]",
        f"[dim]${totals['total_daily_dividend']:.2f}[/dim]",
        "Approximate daily income"
    )

    console.print(frequency_table)
    console.print()

    # Dividend Details Panel
    console.print("[bold bright_green]📅 DIVIDEND PAYMENT DETAILS[/bold bright_green]\n")

    for holding in holdings:
        if holding['annual_dividend_per_share'] > 0:
            console.print(f"[bold green]{holding['ticker']}[/bold green] - {holding['company']}")
            console.print(f"  [green]Payment Frequency:[/green] {holding['payment_frequency']}")
            console.print(f"  [green]Quarterly Income:[/green] [bright_green]${holding['quarterly_dividend_income']:.2f}[/bright_green]")
            console.print(f"  [green]Ex-Dividend Date:[/green] {holding['ex_dividend_date']}")
            console.print(f"  [green]Yield:[/green] {holding['yield_pct']:.3f}%")
            console.print()

    # Income Visualization
    console.print("[bold bright_green]📊 ANNUAL INCOME VISUALIZATION[/bold bright_green]\n")

    max_income = max((h['annual_dividend_income'] for h in holdings), default=0)
    for holding in holdings:
        if holding['annual_dividend_income'] > 0:
            bar_length = int((holding['annual_dividend_income'] / max(max_income, 1)) * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            console.print(f"[bold green]{holding['ticker']:6}[/bold green] [{bar}] [bright_green]${holding['annual_dividend_income']:>7.2f}[/bright_green]")
        else:
            console.print(f"[dim]{holding['ticker']:6}[/dim] [dim]No Dividends[/dim]")

    console.print()

    # Investment Insights
    insights_title = Text("DIVIDEND INVESTMENT INSIGHTS", style="bold bright_cyan")
    console.print(Align.center(insights_title))
    console.print()

    # Calculate insights
    dividend_stocks = [h for h in holdings if h['annual_dividend_per_share'] > 0]
    non_dividend_stocks = [h for h in holdings if h['annual_dividend_per_share'] == 0]

    insights_text = ""

    if dividend_stocks:
        highest_yield = max(dividend_stocks, key=lambda x: x['yield_pct'])
        insights_text += f"[bold green]✓ HIGHEST YIELD:[/bold green] {highest_yield['ticker']} at {highest_yield['yield_pct']:.3f}%\n"

        highest_income = max(dividend_stocks, key=lambda x: x['annual_dividend_income'])
        insights_text += f"[bold green]✓ HIGHEST INCOME:[/bold green] {highest_income['ticker']} generating ${highest_income['annual_dividend_income']:.2f}/year\n"

    if non_dividend_stocks:
        insights_text += f"[yellow]⚠ GROWTH STOCKS:[/yellow] {', '.join(h['ticker'] for h in non_dividend_stocks)} - Focused on capital appreciation\n"

    insights_text += f"\n[bold cyan]Portfolio Dividend Yield: {totals['portfolio_yield_pct']:.3f}%[/bold cyan]\n"

    if totals['portfolio_yield_pct'] >= 2.0:
        insights_text += "[bright_green]This is a strong dividend yield![/bright_green]"
    elif totals['portfolio_yield_pct'] >= 1.0:
        insights_text += "[green]This is a solid dividend yield.[/green]"
    elif totals['portfolio_yield_pct'] > 0:
        insights_text += "[yellow]This is a modest dividend yield - typical for growth-oriented portfolios.[/yellow]"
    else:
        insights_text += "[dim]This is a growth-focused portfolio with minimal dividend income.[/dim]"

    insights_panel = Panel(insights_text, border_style="bright_green", style="on black")
    console.print(insights_panel)
    console.print()

    # Annual Income Projection
    projection_title = Text("ANNUAL INCOME PROJECTION", style="bold bright_cyan")
    console.print(Align.center(projection_title))
    console.print()

    projection_text = (
        f"[bold white]If you hold for 1 year:[/bold white]\n"
        f"[bright_green]Annual Dividend Income: ${totals['total_annual_dividend']:.2f}[/bright_green]\n\n"
        f"[bold white]If you hold for 5 years:[/bold white]\n"
        f"[bright_green]Total Dividend Income: ${totals['total_annual_dividend'] * 5:.2f}[/bright_green]\n"
        f"[dim](Assuming consistent dividend rates)[/dim]\n\n"
        f"[bold white]If you hold for 10 years:[/bold white]\n"
        f"[bright_green]Total Dividend Income: ${totals['total_annual_dividend'] * 10:.2f}[/bright_green]\n"
        f"[dim](Assuming consistent dividend rates)[/dim]"
    )
    projection_panel = Panel(projection_text, border_style="bright_green", style="on black")
    console.print(projection_panel)
    console.print()

    # Summary Callout
    summary_title = Text("DIVIDEND INCOME SUMMARY", style="bold bright_green")
    console.print(Align.center(summary_title))
    console.print()

    summary_callout = (
        f"[bold bright_green]╔════════════════════════════════════════╗[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]  [bold white]YOUR ANNUAL DIVIDEND INCOME[/bold white]              [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]                                    [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]     [bold bright_green]${totals['total_annual_dividend']:>8.2f}[/bold bright_green]  PER YEAR         [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]     [bold cyan]${totals['total_quarterly_dividend']:>8.2f}[/bold cyan]  PER QUARTER      [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]     [bold yellow]${totals['total_monthly_dividend']:>8.2f}[/bold yellow]  PER MONTH        [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]     [dim]${totals['total_daily_dividend']:>8.2f}  PER DAY[/dim]          [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║[/bold bright_green]                                    [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]║  Yield: {totals['portfolio_yield_pct']:>6.3f}%[/bold bright_green]                 [bold bright_green]║[/bold bright_green]\n"
        f"[bold bright_green]╚════════════════════════════════════════╝[/bold bright_green]"
    )
    console.print(summary_callout)

def main():
    """Main execution function."""
    try:
        # Get holdings
        holdings = get_portfolio_holdings()

        # Calculate metrics
        holdings = calculate_dividend_metrics(holdings)

        # Calculate totals
        totals = calculate_portfolio_totals(holdings)

        # Display analysis
        display_dividend_analysis(holdings, totals)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich[/cyan]")

if __name__ == "__main__":
    main()
