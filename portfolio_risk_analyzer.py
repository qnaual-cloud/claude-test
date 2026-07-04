#!/usr/bin/env python3
"""
Portfolio Risk Analyzer
Calculates volatility, drawdown, risk-adjusted returns, and risk score.
Shows if returns justify the risk taken.
"""

from datetime import datetime
import math
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_portfolio_holdings():
    """Get portfolio holdings with historical volatility and beta data."""
    print("Loading portfolio risk data...\n")

    # Portfolio holdings with volatility and beta metrics
    # Beta: measure of stock volatility relative to market (S&P 500)
    # Volatility: annualized standard deviation of returns
    holdings = [
        {
            'ticker': 'TSLA',
            'company': 'Tesla Inc.',
            'shares': 10,
            'current_price': 238.45,
            'position_weight': None,  # Will calculate
            'annual_volatility': 0.55,  # 55% - Very volatile
            'beta': 1.95,  # 1.95x more volatile than market
            'one_year_return': -0.20,  # -20% last year
            'three_year_return': 0.85,  # 85% cumulative
            'five_year_return': 2.15,  # 215% cumulative
            'max_drawdown': -0.75,  # -75% peak to trough
        },
        {
            'ticker': 'AAPL',
            'company': 'Apple Inc.',
            'shares': 5,
            'current_price': 235.50,
            'position_weight': None,
            'annual_volatility': 0.28,  # 28% - Moderate volatility
            'beta': 1.20,  # 1.2x more volatile than market
            'one_year_return': 0.30,  # +30% last year
            'three_year_return': 0.95,  # 95% cumulative
            'five_year_return': 1.85,  # 185% cumulative
            'max_drawdown': -0.35,  # -35% peak to trough
        },
        {
            'ticker': 'NVDA',
            'company': 'NVIDIA Corporation',
            'shares': 8,
            'current_price': 875.00,
            'position_weight': None,
            'annual_volatility': 0.42,  # 42% - High volatility
            'beta': 1.65,  # 1.65x more volatile than market
            'one_year_return': 1.08,  # +108% last year
            'three_year_return': 3.50,  # 350% cumulative
            'five_year_return': 5.25,  # 525% cumulative
            'max_drawdown': -0.60,  # -60% peak to trough
        },
    ]

    return holdings

def calculate_portfolio_metrics(holdings):
    """Calculate portfolio-level risk metrics."""

    # Calculate position values and weights
    total_value = sum(h['shares'] * h['current_price'] for h in holdings)

    for holding in holdings:
        holding['position_value'] = holding['shares'] * holding['current_price']
        holding['position_weight'] = holding['position_value'] / total_value

    # Calculate portfolio-weighted volatility (simplified)
    portfolio_volatility = sum(
        h['position_weight'] * h['annual_volatility']
        for h in holdings
    )

    # Calculate portfolio beta
    portfolio_beta = sum(
        h['position_weight'] * h['beta']
        for h in holdings
    )

    # Calculate portfolio returns (weighted average)
    portfolio_one_year = sum(
        h['position_weight'] * h['one_year_return']
        for h in holdings
    )

    portfolio_three_year = sum(
        h['position_weight'] * h['three_year_return']
        for h in holdings
    )

    portfolio_five_year = sum(
        h['position_weight'] * h['five_year_return']
        for h in holdings
    )

    # Calculate maximum portfolio drawdown (conservative: sum of weights)
    portfolio_max_drawdown = sum(
        h['position_weight'] * h['max_drawdown']
        for h in holdings
    )

    # Risk-free rate (Treasury yield)
    risk_free_rate = 0.045  # 4.5% (approximate current T-Bill rate)

    # Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
    sharpe_ratio = (portfolio_one_year - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0

    # Sortino Ratio (uses downside volatility)
    downside_volatility = portfolio_volatility * 0.65  # Approximate downside vol
    sortino_ratio = (portfolio_one_year - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0

    metrics = {
        'total_value': total_value,
        'portfolio_volatility': portfolio_volatility,
        'portfolio_beta': portfolio_beta,
        'portfolio_one_year_return': portfolio_one_year,
        'portfolio_three_year_return': portfolio_three_year,
        'portfolio_five_year_return': portfolio_five_year,
        'portfolio_max_drawdown': portfolio_max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'risk_free_rate': risk_free_rate,
    }

    return holdings, metrics

def calculate_risk_score(metrics):
    """
    Calculate portfolio risk score (1-10).
    1 = Very conservative (low risk)
    10 = Extremely aggressive (high risk)
    """
    score = 5.0  # Start at neutral

    # Volatility component (40% weight)
    if metrics['portfolio_volatility'] < 0.15:
        score -= 2.0  # Very low volatility
    elif metrics['portfolio_volatility'] < 0.25:
        score -= 1.0
    elif metrics['portfolio_volatility'] < 0.35:
        score += 0.0  # Neutral
    elif metrics['portfolio_volatility'] < 0.50:
        score += 1.5
    elif metrics['portfolio_volatility'] < 0.65:
        score += 2.5
    else:
        score += 3.0  # Very high volatility

    # Beta component (30% weight)
    if metrics['portfolio_beta'] < 0.8:
        score -= 1.5
    elif metrics['portfolio_beta'] < 1.0:
        score -= 0.5
    elif metrics['portfolio_beta'] < 1.3:
        score += 0.5
    elif metrics['portfolio_beta'] < 1.6:
        score += 1.5
    else:
        score += 2.5

    # Drawdown component (30% weight)
    if metrics['portfolio_max_drawdown'] > -0.20:
        score -= 1.0
    elif metrics['portfolio_max_drawdown'] > -0.40:
        score += 0.5
    elif metrics['portfolio_max_drawdown'] > -0.60:
        score += 1.5
    else:
        score += 2.5

    return max(1, min(10, score))

def get_risk_rating(score):
    """Get risk rating based on score."""
    if score <= 2:
        return "VERY CONSERVATIVE", "bright_green"
    elif score <= 3.5:
        return "CONSERVATIVE", "green"
    elif score <= 5:
        return "MODERATE", "yellow"
    elif score <= 6.5:
        return "MODERATELY AGGRESSIVE", "bright_yellow"
    elif score <= 8:
        return "AGGRESSIVE", "bright_red"
    else:
        return "VERY AGGRESSIVE", "bold bright_red"

def get_metric_color(value, metric_type):
    """Get color based on metric value."""
    if metric_type == 'volatility':
        if value < 0.20:
            return "bright_green"
        elif value < 0.35:
            return "green"
        elif value < 0.50:
            return "yellow"
        else:
            return "bright_red"

    elif metric_type == 'beta':
        if value < 0.9:
            return "bright_green"
        elif value < 1.1:
            return "green"
        elif value < 1.3:
            return "yellow"
        else:
            return "bright_red"

    elif metric_type == 'return':
        if value > 0.20:
            return "bright_green"
        elif value > 0.10:
            return "green"
        elif value > 0:
            return "yellow"
        else:
            return "bright_red"

    elif metric_type == 'drawdown':
        if value > -0.20:
            return "bright_green"
        elif value > -0.40:
            return "green"
        elif value > -0.60:
            return "yellow"
        else:
            return "bright_red"

    elif metric_type == 'sharpe':
        if value > 1.0:
            return "bright_green"
        elif value > 0.5:
            return "green"
        elif value > 0:
            return "yellow"
        else:
            return "bright_red"

    return "white"

def display_risk_analysis(holdings, metrics):
    """Display comprehensive risk analysis."""

    # Header
    title = Text("PORTFOLIO RISK ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Risk Score Panel
    risk_score = calculate_risk_score(metrics)
    rating, rating_color = get_risk_rating(risk_score)

    risk_panel_text = (
        f"[{rating_color}]PORTFOLIO RISK SCORE: {risk_score:.1f}/10[/{rating_color}]\n"
        f"[{rating_color}]Risk Profile: {rating}[/{rating_color}]"
    )
    risk_panel = Panel(risk_panel_text, border_style="bright_cyan", style="on black",
                      title="[bold bright_cyan]RISK ASSESSMENT[/bold bright_cyan]")
    console.print(risk_panel)
    console.print()

    # Portfolio Overview
    overview_text = (
        f"[bold white]Portfolio Value:[/bold white] [bright_cyan]${metrics['total_value']:,.2f}[/bright_cyan]\n"
        f"[bold white]Number of Holdings:[/bold white] [bright_cyan]{len(holdings)}[/bright_cyan]\n"
        f"[bold white]Analysis Date:[/bold white] [bright_white]{datetime.now().strftime('%B %d, %Y')}[/bright_white]"
    )
    overview_panel = Panel(overview_text, border_style="cyan", style="on black")
    console.print(overview_panel)
    console.print()

    # Risk Metrics Summary Table
    risk_table = Table(title="[bold bright_cyan]KEY RISK METRICS[/bold bright_cyan]",
                      show_header=True,
                      header_style="bold white on dark_blue",
                      border_style="cyan",
                      padding=(0, 1))

    risk_table.add_column("Metric", style="bold white")
    risk_table.add_column("Value", style="bright_white", justify="right")
    risk_table.add_column("Interpretation", style="white")

    # Volatility
    vol_color = get_metric_color(metrics['portfolio_volatility'], 'volatility')
    risk_table.add_row(
        "[bold]Portfolio Volatility[/bold]",
        f"[{vol_color}]{metrics['portfolio_volatility']*100:.1f}%[/{vol_color}]",
        "Annualized price fluctuation"
    )

    # Beta
    beta_color = get_metric_color(metrics['portfolio_beta'], 'beta')
    beta_interpretation = f"{metrics['portfolio_beta']:.2f}x market volatility"
    risk_table.add_row(
        "[bold]Portfolio Beta[/bold]",
        f"[{beta_color}]{metrics['portfolio_beta']:.2f}[/{beta_color}]",
        beta_interpretation
    )

    # 1-Year Return
    ret_color = get_metric_color(metrics['portfolio_one_year_return'], 'return')
    risk_table.add_row(
        "[bold]1-Year Return[/bold]",
        f"[{ret_color}]{metrics['portfolio_one_year_return']*100:+.1f}%[/{ret_color}]",
        "Annual performance"
    )

    # Maximum Drawdown
    dd_color = get_metric_color(metrics['portfolio_max_drawdown'], 'drawdown')
    risk_table.add_row(
        "[bold]Maximum Drawdown[/bold]",
        f"[{dd_color}]{metrics['portfolio_max_drawdown']*100:.1f}%[/{dd_color}]",
        "Peak-to-trough decline"
    )

    # Sharpe Ratio
    sharpe_color = get_metric_color(metrics['sharpe_ratio'], 'sharpe')
    risk_table.add_row(
        "[bold]Sharpe Ratio[/bold]",
        f"[{sharpe_color}]{metrics['sharpe_ratio']:.2f}[/{sharpe_color}]",
        "Return per unit of risk"
    )

    console.print(risk_table)
    console.print()

    # Individual Stock Risk Analysis
    console.print("[bold bright_cyan]📊 INDIVIDUAL STOCK RISK ANALYSIS[/bold bright_cyan]\n")

    stock_table = Table(show_header=True,
                       header_style="bold white on dark_blue",
                       border_style="cyan",
                       padding=(0, 1))

    stock_table.add_column("Ticker", style="bold white", justify="center")
    stock_table.add_column("Weight", style="bright_cyan", justify="center")
    stock_table.add_column("Volatility", style="bright_white", justify="center")
    stock_table.add_column("Beta", style="bright_white", justify="center")
    stock_table.add_column("1Y Return", style="bright_white", justify="center")
    stock_table.add_column("Max Drawdown", style="bright_white", justify="center")

    for holding in holdings:
        vol_color = get_metric_color(holding['annual_volatility'], 'volatility')
        beta_color = get_metric_color(holding['beta'], 'beta')
        ret_color = get_metric_color(holding['one_year_return'], 'return')
        dd_color = get_metric_color(holding['max_drawdown'], 'drawdown')

        stock_table.add_row(
            holding['ticker'],
            f"{holding['position_weight']*100:.1f}%",
            f"[{vol_color}]{holding['annual_volatility']*100:.0f}%[/{vol_color}]",
            f"[{beta_color}]{holding['beta']:.2f}[/{beta_color}]",
            f"[{ret_color}]{holding['one_year_return']*100:+.0f}%[/{ret_color}]",
            f"[{dd_color}]{holding['max_drawdown']*100:.0f}%[/{dd_color}]"
        )

    console.print(stock_table)
    console.print()

    # Risk Explanation Section
    console.print("[bold bright_cyan]💡 UNDERSTANDING YOUR RISK METRICS[/bold bright_cyan]\n")

    console.print("[bold cyan]Volatility (Annual):[/bold cyan]")
    console.print(f"  Your portfolio volatility is [bright_yellow]{metrics['portfolio_volatility']*100:.1f}%[/bright_yellow]")
    console.print("  This measures how much your portfolio value fluctuates year-to-year.")
    if metrics['portfolio_volatility'] > 0.40:
        console.print("  [bright_red]High volatility = Significant price swings[/bright_red]")
    elif metrics['portfolio_volatility'] > 0.25:
        console.print("  [yellow]Moderate-to-high volatility = Noticeable fluctuations[/yellow]")
    else:
        console.print("  [green]Lower volatility = More stable prices[/green]")
    console.print()

    console.print("[bold cyan]Beta:[/bold cyan]")
    console.print(f"  Your portfolio beta is [bright_yellow]{metrics['portfolio_beta']:.2f}[/bright_yellow]")
    console.print(f"  This means your portfolio moves [bright_yellow]{metrics['portfolio_beta']:.1f}x[/bright_yellow] as much as the S&P 500.")
    if metrics['portfolio_beta'] > 1.5:
        console.print("  [bright_red]Very high beta = Much more volatile than the market[/bright_red]")
    elif metrics['portfolio_beta'] > 1.2:
        console.print("  [yellow]High beta = More volatile than the market[/yellow]")
    else:
        console.print("  [green]Beta near 1 = Similar to market volatility[/green]")
    console.print()

    console.print("[bold cyan]Sharpe Ratio:[/bold cyan]")
    console.print(f"  Your Sharpe ratio is [bright_yellow]{metrics['sharpe_ratio']:.2f}[/bright_yellow]")
    console.print("  This measures return earned per unit of risk taken.")
    if metrics['sharpe_ratio'] > 1.0:
        console.print("  [bright_green]Good: You're earning solid returns for your risk level[/bright_green]")
    elif metrics['sharpe_ratio'] > 0.5:
        console.print("  [yellow]Fair: Returns are adequate for risk taken[/yellow]")
    else:
        console.print("  [bright_red]Poor: You may not be compensated enough for your risk[/bright_red]")
    console.print()

    console.print("[bold cyan]Maximum Drawdown:[/bold cyan]")
    console.print(f"  Your maximum drawdown was [bright_yellow]{metrics['portfolio_max_drawdown']*100:.1f}%[/bright_yellow]")
    console.print("  This is the worst peak-to-trough decline experienced.")
    if metrics['portfolio_max_drawdown'] < -0.60:
        console.print("  [bright_red]Severe: Portfolio lost more than 60% at worst point[/bright_red]")
    elif metrics['portfolio_max_drawdown'] < -0.40:
        console.print("  [bright_yellow]Significant: Portfolio declined 40-60% at worst point[/bright_yellow]")
    else:
        console.print("  [yellow]Moderate: Portfolio declined less than 40% at worst[/yellow]")
    console.print()

    # Return vs Risk Analysis
    console.print("[bold bright_cyan]📈 DO YOUR RETURNS JUSTIFY THE RISK?[/bold bright_cyan]\n")

    # Calculate risk-adjusted metrics
    expected_market_return = 0.10  # 10% expected market return
    excess_return = metrics['portfolio_one_year_return'] - expected_market_return

    analysis_text = (
        f"[bold white]1-Year Portfolio Return:[/bold white] [bright_green]{metrics['portfolio_one_year_return']*100:+.1f}%[/bright_green]\n"
        f"[bold white]Expected Market Return:[/bold white] [bright_yellow]{expected_market_return*100:.1f}%[/bright_yellow]\n"
        f"[bold white]Excess Return:[/bold white] [bright_green]{excess_return*100:+.1f}%[/bright_green]\n"
        f"[bold white]Risk Taken (Volatility):[/bold white] [bright_yellow]{metrics['portfolio_volatility']*100:.1f}%[/bright_yellow]\n"
    )

    if metrics['portfolio_one_year_return'] > expected_market_return * 1.2:
        analysis_text += "[bright_green]✓ YES - Strong returns justify the risk taken[/bright_green]"
    elif metrics['portfolio_one_year_return'] > expected_market_return:
        analysis_text += "[yellow]⚠ MAYBE - Adequate returns but monitor closely[/yellow]"
    else:
        analysis_text += "[bright_red]✗ NO - Returns do not justify the risk level[/bright_red]"

    analysis_panel = Panel(analysis_text, border_style="cyan", style="on black")
    console.print(analysis_panel)
    console.print()

    # Risk Scenarios
    console.print("[bold bright_cyan]⚡ RISK SCENARIOS[/bold bright_cyan]\n")

    # Calculate potential outcomes
    portfolio_value = metrics['total_value']
    best_case = portfolio_value * (1 + metrics['portfolio_volatility'] * 2)  # +2 std devs
    worst_case = portfolio_value * (1 - metrics['portfolio_volatility'] * 2)  # -2 std devs

    scenarios_text = (
        f"[bold white]Current Portfolio Value:[/bold white] [bright_cyan]${portfolio_value:,.2f}[/bright_cyan]\n\n"
        f"[bold bright_green]Best Case Scenario (Optimistic):[/bold bright_green]\n"
        f"  +{metrics['portfolio_volatility']*100*2:.1f}% move = [bright_green]${best_case:,.2f}[/bright_green]\n\n"
        f"[bold bright_red]Worst Case Scenario (Pessimistic):[/bold bright_red]\n"
        f"  -{metrics['portfolio_volatility']*100*2:.1f}% move = [bright_red]${worst_case:,.2f}[/bright_red]\n\n"
        f"[dim]Based on 2 standard deviation move (95% confidence interval)[/dim]"
    )
    scenarios_panel = Panel(scenarios_text, border_style="cyan", style="on black")
    console.print(scenarios_panel)
    console.print()

    # Risk Rating Explanation
    console.print("[bold bright_cyan]🎯 RISK RATING EXPLANATION[/bold bright_cyan]\n")

    rating_guide = (
        f"[bold bright_green]1-2: Very Conservative[/bold bright_green]\n"
        f"  • Low volatility, bonds/dividend stocks\n"
        f"  • Suitable for retirees/risk-averse investors\n\n"
        f"[bold green]3-4: Conservative[/bold green]\n"
        f"  • Moderate volatility, quality stocks\n"
        f"  • Suitable for cautious investors\n\n"
        f"[bold yellow]5: Moderate[/bold yellow]\n"
        f"  • Balanced growth and stability\n"
        f"  • Typical for long-term investors\n\n"
        f"[bold bright_yellow]6-7: Moderately Aggressive[/bold bright_yellow]\n"
        f"  • Higher volatility, growth focus\n"
        f"  • Suitable for long-term investors with higher risk tolerance\n\n"
        f"[bold bright_red]8-9: Aggressive[/bold bright_red]\n"
        f"  • High volatility, concentrated bets\n"
        f"  • Suitable for experienced investors only\n\n"
        f"[bold bold bright_red]10: Very Aggressive[/bold bold bright_red]\n"
        f"  • Extreme volatility, speculative positions\n"
        f"  • High risk of significant losses\n\n"
        f"[bold]Your Rating: {rating} ({risk_score:.1f}/10)[/bold]"
    )
    rating_panel = Panel(rating_guide, border_style="bright_cyan", style="on black")
    console.print(rating_panel)
    console.print()

    # Recommendations
    console.print("[bold bright_cyan]💼 RECOMMENDATIONS[/bold bright_cyan]\n")

    if risk_score <= 3:
        recommendations = (
            "[green]Your portfolio is conservative. Consider:[/green]\n"
            "  • Small allocation to growth stocks for long-term gains\n"
            "  • Monitor fixed income allocation"
        )
    elif risk_score <= 5:
        recommendations = (
            "[yellow]Your portfolio is moderate. Consider:[/yellow]\n"
            "  • Maintain diversification across sectors\n"
            "  • Review allocation annually\n"
            "  • Ensure emergency fund is separate"
        )
    elif risk_score <= 7:
        recommendations = (
            "[bright_yellow]Your portfolio is moderately aggressive. Consider:[/bright_yellow]\n"
            "  • Rebalance quarterly to maintain target allocation\n"
            "  • Have 10+ year investment horizon\n"
            "  • Be prepared for 30-50% drawdowns"
        )
    else:
        recommendations = (
            "[bright_red]Your portfolio is aggressive. Important:[/bright_red]\n"
            "  • Only invest money you won't need for 10+ years\n"
            "  • Be prepared for 60%+ drawdowns\n"
            "  • Consider reducing concentration in single stocks\n"
            "  • Rebalance regularly to manage risk"
        )

    console.print(recommendations)

def main():
    """Main execution function."""
    try:
        # Get holdings
        holdings = get_portfolio_holdings()

        # Calculate metrics
        holdings, metrics = calculate_portfolio_metrics(holdings)

        # Display analysis
        display_risk_analysis(holdings, metrics)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich[/cyan]")

if __name__ == "__main__":
    main()
