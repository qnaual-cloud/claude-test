#!/usr/bin/env python3
"""
Portfolio Performance Analyzer
Calculates portfolio returns and compares against S&P 500 benchmark.
Shows if you're beating the market or underperforming.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def get_portfolio_data():
    """Get sample investor portfolio with entry prices and current prices."""
    print("Loading portfolio data...\n")

    # Sample portfolio - realistic investor holdings
    portfolio = {
        'investor_name': 'Smart Investor Portfolio',
        'portfolio_value': 0,  # Will calculate
        'entry_date': '2023-01-15',
        'current_date': '2026-06-17',
        'holdings': [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'shares': 50,
                'entry_price': 150.25,
                'current_price': 235.50,
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft',
                'shares': 30,
                'entry_price': 300.00,
                'current_price': 425.75,
            },
            {
                'ticker': 'NVDA',
                'name': 'NVIDIA',
                'shares': 20,
                'entry_price': 200.00,
                'current_price': 875.00,
            },
            {
                'ticker': 'GOOGL',
                'name': 'Alphabet',
                'shares': 25,
                'entry_price': 90.00,
                'current_price': 185.25,
            },
            {
                'ticker': 'TSLA',
                'name': 'Tesla',
                'shares': 15,
                'entry_price': 800.00,
                'current_price': 238.45,
            },
            {
                'ticker': 'META',
                'name': 'Meta Platforms',
                'shares': 35,
                'entry_price': 250.00,
                'current_price': 520.00,
            },
            {
                'ticker': 'AMZN',
                'name': 'Amazon',
                'shares': 40,
                'entry_price': 145.00,
                'current_price': 200.50,
            },
            {
                'ticker': 'JPM',
                'name': 'JPMorgan Chase',
                'shares': 60,
                'entry_price': 120.00,
                'current_price': 185.75,
            },
            {
                'ticker': 'V',
                'name': 'Visa',
                'shares': 45,
                'entry_price': 220.00,
                'current_price': 295.50,
            },
            {
                'ticker': 'JNJ',
                'name': 'Johnson & Johnson',
                'shares': 35,
                'entry_price': 155.00,
                'current_price': 164.25,
            },
        ]
    }

    return portfolio

def calculate_position_metrics(holding):
    """Calculate metrics for a single position."""
    entry_value = holding['shares'] * holding['entry_price']
    current_value = holding['shares'] * holding['current_price']
    gain_loss = current_value - entry_value
    gain_loss_pct = (gain_loss / entry_value) * 100

    return {
        'entry_value': entry_value,
        'current_value': current_value,
        'gain_loss': gain_loss,
        'gain_loss_pct': gain_loss_pct,
    }

def calculate_portfolio_metrics(portfolio):
    """Calculate overall portfolio metrics."""
    total_entry_value = 0
    total_current_value = 0
    total_gain_loss = 0

    for holding in portfolio['holdings']:
        metrics = calculate_position_metrics(holding)
        holding['metrics'] = metrics
        total_entry_value += metrics['entry_value']
        total_current_value += metrics['current_value']
        total_gain_loss += metrics['gain_loss']

    portfolio['total_entry_value'] = total_entry_value
    portfolio['total_current_value'] = total_current_value
    portfolio['total_gain_loss'] = total_gain_loss
    portfolio['total_return_pct'] = (total_gain_loss / total_entry_value) * 100

    return portfolio

def get_benchmark_data():
    """Get S&P 500 benchmark data for comparison."""
    # S&P 500 performance over the same period (Jan 2023 - Jun 2026)
    # Approximate data: ~3.5 year period

    benchmark = {
        'name': 'S&P 500',
        'entry_date': '2023-01-15',
        'entry_price': 3800.00,  # Approximate SPY entry
        'current_price': 5475.00,  # Approximate current level
        'entry_value': 100000,  # Hypothetical $100k investment
    }

    current_value = benchmark['entry_value'] * (benchmark['current_price'] / benchmark['entry_price'])
    gain_loss = current_value - benchmark['entry_value']
    return_pct = (gain_loss / benchmark['entry_value']) * 100

    benchmark['current_value'] = current_value
    benchmark['gain_loss'] = gain_loss
    benchmark['return_pct'] = return_pct

    return benchmark

def calculate_performance_score(portfolio_return, benchmark_return, portfolio_volatility=0.18):
    """
    Calculate portfolio performance score (1-10).
    Considers:
    - Alpha (outperformance vs benchmark)
    - Risk-adjusted returns (Sharpe ratio)
    - Consistency
    """
    score = 5.0  # Start at neutral

    # Alpha: How much better/worse than benchmark (weight: 60%)
    alpha = portfolio_return - benchmark_return
    if alpha > 20:
        score += 3.0
    elif alpha > 10:
        score += 2.0
    elif alpha > 5:
        score += 1.0
    elif alpha > 0:
        score += 0.5
    elif alpha > -5:
        score -= 0.5
    elif alpha > -10:
        score -= 1.0
    else:
        score -= 2.0

    # Risk-adjusted metric (weight: 40%)
    # Lower volatility with positive returns is better
    risk_adjusted = portfolio_return / max(portfolio_volatility, 0.01)
    if risk_adjusted > 2.0:
        score += 1.5
    elif risk_adjusted > 1.0:
        score += 0.75
    elif risk_adjusted > 0:
        score += 0.25
    else:
        score -= 0.5

    return max(1, min(10, score))

def get_performance_rating(score):
    """Get rating description based on score."""
    if score >= 8.5:
        return "EXCEPTIONAL", "bright_green"
    elif score >= 7.5:
        return "EXCELLENT", "green"
    elif score >= 6.5:
        return "VERY GOOD", "cyan"
    elif score >= 5.5:
        return "GOOD", "yellow"
    elif score >= 4.5:
        return "FAIR", "bright_yellow"
    elif score >= 3.5:
        return "POOR", "bright_red"
    else:
        return "VERY POOR", "bold bright_red"

def get_return_color(return_pct):
    """Get color based on return percentage."""
    if return_pct >= 50:
        return "bright_green"
    elif return_pct >= 30:
        return "green"
    elif return_pct >= 15:
        return "cyan"
    elif return_pct >= 5:
        return "yellow"
    elif return_pct >= 0:
        return "bright_yellow"
    elif return_pct >= -10:
        return "bright_red"
    else:
        return "bold bright_red"

def display_portfolio_analysis(portfolio, benchmark):
    """Display comprehensive portfolio analysis."""

    # Header
    title = Text("PORTFOLIO PERFORMANCE ANALYZER", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Portfolio Summary Panel
    portfolio_color = get_return_color(portfolio['total_return_pct'])
    summary_text = (f"[bold white]Portfolio Value:[/bold white] [bright_cyan]${portfolio['total_current_value']:,.0f}[/bright_cyan]\n"
                   f"[bold white]Total Invested:[/bold white] [bright_yellow]${portfolio['total_entry_value']:,.0f}[/bright_yellow]\n"
                   f"[bold white]Total Gain/Loss:[/bold white] [{portfolio_color}]${portfolio['total_gain_loss']:,.0f} ({portfolio['total_return_pct']:.2f}%)[/{portfolio_color}]\n"
                   f"[bold white]Time Period:[/bold white] [bright_white]{portfolio['entry_date']} → {portfolio['current_date']}[/bright_white]")
    portfolio_panel = Panel(summary_text, border_style="cyan", style="on black", title="[bold cyan]YOUR PORTFOLIO[/bold cyan]")
    console.print(portfolio_panel)
    console.print()

    # Benchmark Summary Panel
    benchmark_color = get_return_color(benchmark['return_pct'])
    benchmark_text = (f"[bold white]Benchmark Value:[/bold white] [bright_cyan]${benchmark['current_value']:,.0f}[/bright_cyan]\n"
                     f"[bold white]Initial Investment:[/bold white] [bright_yellow]${benchmark['entry_value']:,.0f}[/bright_yellow]\n"
                     f"[bold white]Total Gain/Loss:[/bold white] [{benchmark_color}]${benchmark['gain_loss']:,.0f} ({benchmark['return_pct']:.2f}%)[/{benchmark_color}]\n"
                     f"[bold white]Index:[/bold white] [bright_white]S&P 500 (SPY)[/bright_white]")
    benchmark_panel = Panel(benchmark_text, border_style="cyan", style="on black", title="[bold cyan]S&P 500 BENCHMARK[/bold cyan]")
    console.print(benchmark_panel)
    console.print()

    # Performance Comparison
    alpha = portfolio['total_return_pct'] - benchmark['return_pct']
    alpha_color = "bright_green" if alpha >= 0 else "bright_red"

    comparison_text = (f"[bold white]Portfolio Return:[/bold white] [{portfolio_color}]{portfolio['total_return_pct']:.2f}%[/{portfolio_color}]\n"
                      f"[bold white]Benchmark Return:[/bold white] [{benchmark_color}]{benchmark['return_pct']:.2f}%[/{benchmark_color}]\n"
                      f"[bold white]Alpha (Outperformance):[/bold white] [{alpha_color}]{alpha:+.2f}%[/{alpha_color}]\n")

    if alpha >= 0:
        comparison_text += f"[bright_green]✓ You are BEATING the market![/bright_green]"
    else:
        comparison_text += f"[bright_red]✗ You are UNDERPERFORMING the market[/bright_red]"

    comparison_panel = Panel(comparison_text, border_style="cyan", style="on black", title="[bold cyan]PERFORMANCE COMPARISON[/bold cyan]")
    console.print(comparison_panel)
    console.print()

    # Holdings Table
    holdings_table = Table(title="[bold cyan]PORTFOLIO HOLDINGS[/bold cyan]",
                          show_header=True,
                          header_style="bold white on dark_blue",
                          border_style="cyan",
                          padding=(0, 1))

    holdings_table.add_column("Ticker", style="bold white", justify="center")
    holdings_table.add_column("Company", style="bright_white")
    holdings_table.add_column("Shares", style="bright_cyan", justify="center")
    holdings_table.add_column("Entry Price", style="bright_yellow", justify="right")
    holdings_table.add_column("Current Price", style="bright_yellow", justify="right")
    holdings_table.add_column("Current Value", style="bright_cyan", justify="right")
    holdings_table.add_column("Return", style="bold white", justify="center")

    for holding in sorted(portfolio['holdings'], key=lambda x: x['metrics']['gain_loss_pct'], reverse=True):
        metrics = holding['metrics']
        return_color = get_return_color(metrics['gain_loss_pct'])

        holdings_table.add_row(
            holding['ticker'],
            holding['name'],
            str(holding['shares']),
            f"${holding['entry_price']:.2f}",
            f"${holding['current_price']:.2f}",
            f"${metrics['current_value']:,.0f}",
            f"[{return_color}]{metrics['gain_loss_pct']:+.2f}%[/{return_color}]"
        )

    console.print(holdings_table)
    console.print()

    # Performance Score
    performance_score = calculate_performance_score(
        portfolio['total_return_pct'],
        benchmark['return_pct']
    )
    rating, rating_color = get_performance_rating(performance_score)

    score_text = (f"[{rating_color}]PERFORMANCE SCORE: {performance_score:.1f}/10[/{rating_color}]\n"
                 f"[{rating_color}]Rating: {rating}[/{rating_color}]")
    score_panel = Panel(score_text, border_style="cyan", style="on black", title="[bold cyan]INVESTOR SKILL SCORE[/bold cyan]")
    console.print(score_panel)
    console.print()

    # Top Performers
    console.print("[bold bright_cyan]🏆 TOP PERFORMERS[/bold bright_cyan]\n")
    top_3 = sorted(portfolio['holdings'], key=lambda x: x['metrics']['gain_loss_pct'], reverse=True)[:3]

    for idx, holding in enumerate(top_3, 1):
        metrics = holding['metrics']
        return_color = get_return_color(metrics['gain_loss_pct'])
        console.print(f"[bold cyan]{idx}. {holding['name']} ({holding['ticker']})[/bold cyan]")
        console.print(f"   Return: [{return_color}]{metrics['gain_loss_pct']:+.2f}%[/{return_color}]  "
                     f"Gain: [bright_green]${metrics['gain_loss']:+,.0f}[/bright_green]")
        console.print()

    # Worst Performers
    console.print("[bold bright_red]⚠️ WORST PERFORMERS[/bold bright_red]\n")
    bottom_3 = sorted(portfolio['holdings'], key=lambda x: x['metrics']['gain_loss_pct'])[:3]

    for idx, holding in enumerate(bottom_3, 1):
        metrics = holding['metrics']
        return_color = get_return_color(metrics['gain_loss_pct'])
        console.print(f"[bold red]{idx}. {holding['name']} ({holding['ticker']})[/bold red]")
        console.print(f"   Return: [{return_color}]{metrics['gain_loss_pct']:+.2f}%[/{return_color}]  "
                     f"Loss: [bright_red]${metrics['gain_loss']:+,.0f}[/bright_red]")
        console.print()

    # Market Insight Analysis
    analysis_title = Text("MARKET PERFORMANCE ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(analysis_title))
    console.print()

    # Calculate statistics
    all_returns = [holding['metrics']['gain_loss_pct'] for holding in portfolio['holdings']]
    avg_return = sum(all_returns) / len(all_returns)
    best_return = max(all_returns)
    worst_return = min(all_returns)

    console.print(f"[bold cyan]📊 PORTFOLIO STATISTICS[/bold cyan]")
    console.print(f"  Average Position Return:  [bright_yellow]{avg_return:.2f}%[/bright_yellow]")
    console.print(f"  Best Position:            [{get_return_color(best_return)}]{best_return:.2f}%[/{get_return_color(best_return)}]")
    console.print(f"  Worst Position:           [{get_return_color(worst_return)}]{worst_return:.2f}%[/{get_return_color(worst_return)}]")
    console.print(f"  Number of Holdings:       [bright_white]{len(portfolio['holdings'])}[/bright_white]")
    console.print()

    # Positions beating benchmark
    beating_benchmark = sum(1 for h in portfolio['holdings'] if h['metrics']['gain_loss_pct'] > benchmark['return_pct'])
    pct_beating = (beating_benchmark / len(portfolio['holdings'])) * 100

    console.print(f"[bold cyan]🎯 BENCHMARK COMPARISON[/bold cyan]")
    console.print(f"  S&P 500 Return:           [{benchmark_color}]{benchmark['return_pct']:.2f}%[/{benchmark_color}]")
    console.print(f"  Your Portfolio Return:    [{portfolio_color}]{portfolio['total_return_pct']:.2f}%[/{portfolio_color}]")
    console.print(f"  Outperformance (Alpha):   [{alpha_color}]{alpha:+.2f}%[/{alpha_color}]")
    console.print(f"  Holdings Beating Market:  [bright_yellow]{beating_benchmark}/{len(portfolio['holdings'])} ({pct_beating:.0f}%)[/bright_yellow]")
    console.print()

    # Investment Conclusion
    conclusion_title = Text("INVESTMENT CONCLUSIONS", style="bold bright_cyan")
    console.print(Align.center(conclusion_title))
    console.print()

    if alpha >= 15:
        conclusion = (f"[bold bright_green]EXCEPTIONAL PERFORMANCE[/bold bright_green]\n\n"
                     f"Your portfolio has significantly outperformed the S&P 500 by {alpha:.2f} percentage points.\n"
                     f"This suggests strong stock-picking ability and excellent market timing.\n\n"
                     f"[bright_green]Key Strengths:[/bright_green]\n"
                     f"[bright_green]•[/bright_green] Significant outperformance vs benchmark\n"
                     f"[bright_green]•[/bright_green] {pct_beating:.0f}% of holdings beating the market\n"
                     f"[bright_green]•[/bright_green] Strong risk-adjusted returns\n\n"
                     f"[yellow]Note:[/yellow] Past performance is not guaranteed to continue. Monitor holdings regularly.")

    elif alpha >= 5:
        conclusion = (f"[bold green]SOLID PERFORMANCE[/bold green]\n\n"
                     f"Your portfolio has outperformed the S&P 500 by {alpha:.2f} percentage points.\n"
                     f"This indicates good stock selection and reasonable market judgment.\n\n"
                     f"[green]Key Observations:[/green]\n"
                     f"[green]•[/green] Consistent outperformance of benchmark\n"
                     f"[green]•[/green] {pct_beating:.0f}% of holdings beating the market\n"
                     f"[green]•[/green] Good portfolio construction\n\n"
                     f"[yellow]Recommendation:[/yellow] Continue current strategy while monitoring changes.")

    elif alpha >= -5:
        conclusion = (f"[bold yellow]MIXED PERFORMANCE[/bold yellow]\n\n"
                     f"Your portfolio is approximately in line with the S&P 500 (Alpha: {alpha:+.2f}%).\n"
                     f"Consider whether active management is worth the effort and costs.\n\n"
                     f"[yellow]Key Observations:[/yellow]\n"
                     f"[yellow]•[/yellow] Performance tracking benchmark\n"
                     f"[yellow]•[/yellow] {pct_beating:.0f}% of holdings beating the market\n"
                     f"[yellow]•[/yellow] Limited edge vs passive strategy\n\n"
                     f"[bright_yellow]Consider:[/bright_yellow] Low-cost index fund alternatives (e.g., SPY, VOO)")

    else:
        conclusion = (f"[bold bright_red]UNDERPERFORMANCE ALERT[/bold bright_red]\n\n"
                     f"Your portfolio is significantly underperforming the S&P 500 by {abs(alpha):.2f} percentage points.\n"
                     f"This suggests stock-picking challenges or poor market timing.\n\n"
                     f"[bright_red]Key Concerns:[/bright_red]\n"
                     f"[bright_red]•[/bright_red] Consistent underperformance vs benchmark\n"
                     f"[bright_red]•[/bright_red] Only {pct_beating:.0f}% of holdings beating the market\n"
                     f"[bright_red]•[/bright_red] Negative alpha indicates poor selection\n\n"
                     f"[bright_yellow]Strong Recommendation:[/bright_yellow] Consider switching to low-cost index funds.")

    conclusion_panel = Panel(conclusion, border_style="cyan", style="on black")
    console.print(conclusion_panel)
    console.print()

    # The Hard Truth
    truth_title = Text("THE HARD TRUTH ABOUT BEATING THE MARKET", style="bold bright_cyan")
    console.print(Align.center(truth_title))
    console.print()

    truth_text = (f"[bold]Research Facts:[/bold]\n"
                 f"[dim]•[/dim] [dim]90% of active fund managers underperform the S&P 500 over 10+ years[/dim]\n"
                 f"[dim]•[/dim] [dim]Individual investors underperform even more due to emotions & timing[/dim]\n"
                 f"[dim]•[/dim] [dim]Beating the market by 10%+ annually is extremely rare & unsustainable[/dim]\n"
                 f"[dim]•[/dim] [dim]After fees/taxes, outperformance becomes even harder[/dim]\n\n"
                 f"[bright_cyan]Your Score: {performance_score:.1f}/10[/bright_cyan] tells you if you're the exception or the rule.\n"
                 f"[bright_cyan]Scores 7+:[/bright_cyan] You likely have genuine edge. [green]Keep going.[/green]\n"
                 f"[bright_cyan]Scores 5-7:[/bright_cyan] You're average. [yellow]Consider low-cost indexing.[/yellow]\n"
                 f"[bright_cyan]Scores <5:[/bright_cyan] You're underperforming. [bright_red]Serious evaluation needed.[/bright_red]")

    truth_panel = Panel(truth_text, border_style="cyan", style="on black")
    console.print(truth_panel)

def main():
    """Main execution function."""
    try:
        # Get portfolio and benchmark data
        portfolio = get_portfolio_data()
        benchmark = get_benchmark_data()

        # Calculate metrics
        portfolio = calculate_portfolio_metrics(portfolio)

        # Display analysis
        display_portfolio_analysis(portfolio, benchmark)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich[/cyan]")

if __name__ == "__main__":
    main()
