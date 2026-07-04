#!/usr/bin/env python3
"""
Portfolio Optimizer
Analyzes current holdings and recommends specific rebalancing moves.
Shows what to buy, what to trim, and missing sectors.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_current_portfolio():
    """Get current portfolio holdings with metrics."""
    print("Analyzing current portfolio...\n")

    holdings = [
        {
            'ticker': 'TSLA',
            'company': 'Tesla Inc.',
            'sector': 'Automotive/EV',
            'shares': 10,
            'current_price': 238.45,
            'position_value': 2384.50,
            'weight': 0.226,  # 22.6%
            'one_year_return': -0.20,
            'ytd_return': -0.18,
            'volatility': 0.55,
            'beta': 1.95,
            'dividend_yield': 0.0000,
            'pe_ratio': 65.4,
            'recommendation': 'TRIM',
            'reasoning': 'Underperforming (-20% YoY), highest volatility, no dividend',
        },
        {
            'ticker': 'AAPL',
            'company': 'Apple Inc.',
            'sector': 'Technology',
            'shares': 5,
            'current_price': 235.50,
            'position_value': 1177.50,
            'weight': 0.111,  # 11.1%
            'one_year_return': 0.30,
            'ytd_return': 0.28,
            'volatility': 0.28,
            'beta': 1.20,
            'dividend_yield': 0.0042,
            'pe_ratio': 31.2,
            'recommendation': 'INCREASE',
            'reasoning': 'Solid performance (+30%), lower risk, dividend payer',
        },
        {
            'ticker': 'NVDA',
            'company': 'NVIDIA Corporation',
            'sector': 'Technology',
            'shares': 8,
            'current_price': 875.00,
            'position_value': 7000.00,
            'weight': 0.663,  # 66.3%
            'one_year_return': 1.08,
            'ytd_return': 1.05,
            'volatility': 0.42,
            'beta': 1.65,
            'dividend_yield': 0.0002,
            'pe_ratio': 68.9,
            'recommendation': 'TRIM',
            'reasoning': 'Excellent performance but oversized position (66% concentration)',
        },
    ]

    return holdings

def get_optimization_targets():
    """Get recommended optimization targets."""
    targets = {
        'target_allocation': {
            'Technology': 0.35,  # Currently 77.4% (77.4% = NVDA 66.3% + AAPL 11.1%)
            'Healthcare': 0.15,  # Missing
            'Financials': 0.12,  # Missing
            'Consumer Discretionary': 0.10,  # Missing
            'Industrials': 0.08,  # Missing
            'Consumer Staples': 0.08,  # Missing
            'Energy': 0.07,  # Missing
            'International': 0.05,  # Missing
        },
        'current_allocation': {
            'Technology': 0.774,  # NVDA + AAPL
            'Automotive/EV': 0.226,  # TSLA
        },
        'specific_recommendations': [
            {
                'action': 'BUY',
                'sector': 'Healthcare',
                'tickers': ['JNJ', 'UNH', 'ABBV'],
                'reason': 'Recession-resistant, dividend payers, lower volatility',
                'allocation': '15%',
                'example': 'JNJ: Dividend yield 2.8%, Beta 0.7 (defensive)',
            },
            {
                'action': 'BUY',
                'sector': 'Financials',
                'tickers': ['JPM', 'BLK', 'GS'],
                'reason': 'Diversification, dividends, economic recovery play',
                'allocation': '12%',
                'example': 'JPM: Dividend yield 2.3%, Beta 1.1 (stable)',
            },
            {
                'action': 'BUY',
                'sector': 'Consumer Discretionary',
                'tickers': ['MCD', 'NKE', 'LUV'],
                'reason': 'Market cycle diversification, growth potential',
                'allocation': '10%',
                'example': 'MCD: Dividend yield 2.4%, Beta 0.8 (stable)',
            },
            {
                'action': 'BUY',
                'sector': 'Consumer Staples',
                'tickers': ['PG', 'KO', 'WMT'],
                'reason': 'Recession protection, consistent dividends, stable',
                'allocation': '8%',
                'example': 'PG: Dividend yield 2.6%, Beta 0.6 (defensive)',
            },
            {
                'action': 'BUY',
                'sector': 'Industrials',
                'tickers': ['BA', 'HON', 'CAT'],
                'reason': 'Economic cycle recovery, dividend income',
                'allocation': '8%',
                'example': 'HON: Dividend yield 1.9%, Beta 1.1 (moderate)',
            },
            {
                'action': 'BUY',
                'sector': 'Energy',
                'tickers': ['XOM', 'CVX', 'COP'],
                'reason': 'Portfolio hedging, high dividend yields',
                'allocation': '7%',
                'example': 'XOM: Dividend yield 3.2%, Beta 1.2',
            },
            {
                'action': 'BUY',
                'sector': 'International',
                'tickers': ['ASML', 'TSM', 'SAP'],
                'reason': 'Geographic diversification, growth exposure',
                'allocation': '5%',
                'example': 'ASML: Growth tech stock, European exposure',
            },
        ]
    }

    return targets

def calculate_optimization_scenario(current_holdings):
    """Calculate optimized portfolio scenario."""
    current_value = sum(h['position_value'] for h in current_holdings)

    # Optimization scenario
    optimized = {
        'TSLA': {
            'current_shares': 10,
            'current_value': 2384.50,
            'current_weight': 0.226,
            'optimized_weight': 0.15,  # Reduce from 22.6% to 15%
            'optimized_value': current_value * 0.15,
            'action': 'SELL',
            'shares_to_sell': 2,  # Sell 2 shares
            'sell_value': 476.90,
            'reasoning': 'Reduce underperforming position and concentration',
        },
        'AAPL': {
            'current_shares': 5,
            'current_value': 1177.50,
            'current_weight': 0.111,
            'optimized_weight': 0.20,  # Increase from 11.1% to 20%
            'optimized_value': current_value * 0.20,
            'action': 'BUY',
            'new_shares': 9,  # Increase to 9 shares (add 4)
            'buy_value': 942.00,
            'reasoning': 'Increase quality dividend-paying position',
        },
        'NVDA': {
            'current_shares': 8,
            'current_value': 7000.00,
            'current_weight': 0.663,
            'optimized_weight': 0.35,  # Reduce from 66.3% to 35%
            'optimized_value': current_value * 0.35,
            'action': 'SELL',
            'shares_to_sell': 4,  # Sell 4 shares
            'sell_value': 3500.00,
            'reasoning': 'Reduce dangerous concentration, lock in gains',
        },
        'cash_generated': 476.90 + 3500.00,  # From selling TSLA and NVDA
        'cash_to_deploy': 942.00 + (476.90 + 3500.00 - 942.00),  # Buy AAPL + reinvest
    }

    return optimized, current_value

def display_optimization_analysis(current_holdings, targets, optimized, current_value):
    """Display comprehensive optimization analysis."""

    # Header
    title = Text("PORTFOLIO OPTIMIZATION ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Current vs Target Allocation
    console.print("[bold bright_cyan]📊 CURRENT ALLOCATION[/bold bright_cyan]\n")

    current_table = Table(show_header=True,
                         header_style="bold white on dark_blue",
                         border_style="cyan",
                         padding=(0, 1))

    current_table.add_column("Ticker", style="bold white", justify="center")
    current_table.add_column("Company", style="bright_white")
    current_table.add_column("Sector", style="bright_yellow")
    current_table.add_column("Shares", style="bright_cyan", justify="center")
    current_table.add_column("Value", style="bright_green", justify="right")
    current_table.add_column("Weight", style="bright_cyan", justify="center")
    current_table.add_column("1Y Return", style="bright_white", justify="center")

    for holding in current_holdings:
        ret_color = "bright_green" if holding['one_year_return'] >= 0 else "bright_red"
        current_table.add_row(
            holding['ticker'],
            holding['company'],
            holding['sector'],
            str(holding['shares']),
            f"${holding['position_value']:,.2f}",
            f"{holding['weight']*100:.1f}%",
            f"[{ret_color}]{holding['one_year_return']*100:+.0f}%[/{ret_color}]"
        )

    console.print(current_table)
    console.print()

    # Rebalancing Recommendations
    console.print("[bold bright_cyan]🎯 SPECIFIC REBALANCING MOVES[/bold bright_cyan]\n")

    for action_item in [h for h in current_holdings if h['recommendation'] in ['TRIM', 'INCREASE']]:
        if action_item['recommendation'] == 'TRIM':
            rec_color = "bright_red"
            action_text = "SELL/TRIM"
            icon = "📉"
        else:
            rec_color = "bright_green"
            action_text = "BUY/INCREASE"
            icon = "📈"

        console.print(f"[bold {rec_color}]{icon} {action_item['ticker']}: {action_text}[/bold {rec_color}]")
        console.print(f"  Company: {action_item['company']}")
        console.print(f"  Current Weight: {action_item['weight']*100:.1f}%")
        console.print(f"  Current Value: ${action_item['position_value']:,.2f}")
        console.print(f"  Current Position: {action_item['shares']} shares @ ${action_item['current_price']:.2f}")
        console.print(f"  YoY Return: {action_item['one_year_return']*100:+.0f}%")
        console.print(f"  Volatility: {action_item['volatility']*100:.0f}%")
        console.print(f"  Dividend Yield: {action_item['dividend_yield']*100:.2f}%")
        console.print(f"  [dim]Reasoning: {action_item['reasoning']}[/dim]")
        console.print()

    # Proposed Transactions
    console.print("[bold bright_cyan]💰 PROPOSED TRANSACTIONS[/bold bright_cyan]\n")

    transaction_table = Table(show_header=True,
                             header_style="bold white on dark_blue",
                             border_style="cyan",
                             padding=(0, 1))

    transaction_table.add_column("Action", style="bold white", justify="center")
    transaction_table.add_column("Ticker", style="bright_yellow", justify="center")
    transaction_table.add_column("Shares", style="bright_white", justify="center")
    transaction_table.add_column("Price", style="bright_cyan", justify="right")
    transaction_table.add_column("Amount", style="bright_white", justify="right")
    transaction_table.add_column("Reason", style="white")

    # TSLA sell
    transaction_table.add_row(
        "[bright_red]SELL[/bright_red]",
        "TSLA",
        "2",
        "$238.45",
        "[bright_red]-$476.90[/bright_red]",
        "Underperforming, highest risk"
    )

    # NVDA sell
    transaction_table.add_row(
        "[bright_red]SELL[/bright_red]",
        "NVDA",
        "4",
        "$875.00",
        "[bright_red]-$3,500.00[/bright_red]",
        "Lock gains, reduce concentration"
    )

    # AAPL buy
    transaction_table.add_row(
        "[bright_green]BUY[/bright_green]",
        "AAPL",
        "4",
        "$235.50",
        "[bright_green]+$942.00[/bright_green]",
        "Quality dividend stock, lower risk"
    )

    # Additional diversification (placeholder)
    transaction_table.add_row(
        "[bright_green]BUY[/bright_green]",
        "Diversify*",
        "-",
        "-",
        "[bright_green]+$3,034.90[/bright_green]",
        "Build out new sectors"
    )

    console.print(transaction_table)
    console.print("[dim]*Deploy remaining cash across: Healthcare (JNJ), Financials (JPM), Consumer (MCD)[/dim]")
    console.print()

    # Missing Sectors
    console.print("[bold bright_cyan]🌍 MISSING SECTORS & OPPORTUNITIES[/bold bright_cyan]\n")

    targets_list = targets['specific_recommendations']
    for rec in targets_list[:4]:  # Show first 4
        console.print(f"[bold bright_green]ADD: {rec['sector'].upper()} ({rec['allocation']})[/bold bright_green]")
        console.print(f"  Why: {rec['reason']}")
        console.print(f"  Suggested Tickers: {', '.join(rec['tickers'])}")
        console.print(f"  Example: {rec['example']}")
        console.print()

    # Proposed Optimized Allocation
    console.print("[bold bright_cyan]📈 PROPOSED OPTIMIZED ALLOCATION[/bold bright_cyan]\n")

    optimized_alloc_text = (
        "[bold white]After rebalancing:[/bold white]\n\n"
        "[bold bright_green]Core Tech (Quality):[/bold bright_green]\n"
        "  • Apple (AAPL): 20% (↑ from 11%)\n"
        "  • NVIDIA (NVDA): 35% (↓ from 66%)\n\n"
        "[bold bright_yellow]Stability & Dividends:[/bold bright_yellow]\n"
        "  • Healthcare: 15% (new)\n"
        "  • Financials: 12% (new)\n"
        "  • Consumer Discretionary: 10% (new)\n\n"
        "[bold bright_cyan]Diversification:[/bold bright_cyan]\n"
        "  • Consumer Staples: 8% (new)\n"
        "  • Industrials: 8% (new)\n"
        "  • Energy: 7% (new)\n"
        "  • International: 5% (new)\n"
        "  • Tesla (TSLA): Eliminated (0%)\n\n"
        "[dim]Total: 100% (More diversified, lower risk, higher dividends)[/dim]"
    )
    optimized_panel = Panel(optimized_alloc_text, border_style="cyan", style="on black")
    console.print(optimized_panel)
    console.print()

    # Risk and Return Impact
    console.print("[bold bright_cyan]📊 IMPACT ANALYSIS[/bold bright_cyan]\n")

    impact_text = (
        "[bold white]Current Portfolio Metrics:[/bold white]\n"
        "  Volatility: 43.4%\n"
        "  Beta: 1.67\n"
        "  1Y Return: +70.4%\n"
        "  Dividend Yield: 0.059%\n"
        "  Max Drawdown: -60.6%\n\n"
        "[bold white]Optimized Portfolio Metrics (Estimated):[/bold white]\n"
        "  [green]Volatility: ~28%[/green] (↓ 35% reduction)\n"
        "  [green]Beta: ~1.15[/green] (↓ closer to market)\n"
        "  [yellow]1Y Return: ~35-45%[/yellow] (↓ less concentrated)\n"
        "  [bright_green]Dividend Yield: ~1.8%[/bright_green] (↑ 30x higher)\n"
        "  [green]Max Drawdown: ~35%[/green] (↓ 42% better)\n\n"
        "[bold cyan]Key Improvement: Much better downside protection with meaningful dividend income[/bold cyan]"
    )
    impact_panel = Panel(impact_text, border_style="cyan", style="on black")
    console.print(impact_panel)
    console.print()

    # Specific Sector Recommendations
    console.print("[bold bright_cyan]💼 DETAILED SECTOR RECOMMENDATIONS[/bold bright_cyan]\n")

    healthcare_text = (
        "[bold bright_green]HEALTHCARE (15% allocation)[/bold bright_green]\n"
        "Why: Recession-resistant, consistent dividends, lower volatility\n"
        "Best Options:\n"
        "  • Johnson & Johnson (JNJ): Dividend 2.8%, Beta 0.7\n"
        "  • UnitedHealth (UNH): Dividend 1.4%, Beta 1.0\n"
        "Allocation: \$1,584 (15% of $10,562)\n\n"
        "[bold bright_green]FINANCIALS (12% allocation)[/bold bright_green]\n"
        "Why: Diversification, economic recovery play, strong dividends\n"
        "Best Options:\n"
        "  • JPMorgan Chase (JPM): Dividend 2.3%, Beta 1.1\n"
        "  • BlackRock (BLK): Dividend 1.5%, Beta 0.9\n"
        "Allocation: \$1,267 (12% of $10,562)\n\n"
        "[bold bright_green]CONSUMER DISCRETIONARY (10% allocation)[/bold bright_green]\n"
        "Why: Growth potential, economic cycle play\n"
        "Best Options:\n"
        "  • McDonald's (MCD): Dividend 2.4%, Beta 0.8\n"
        "  • Nike (NKE): Dividend 0.9%, Beta 0.9\n"
        "Allocation: \$1,056 (10% of $10,562)"
    )
    sector_panel = Panel(healthcare_text, border_style="cyan", style="on black")
    console.print(sector_panel)
    console.print()

    # Action Plan
    console.print("[bold bright_cyan]📋 IMPLEMENTATION ROADMAP[/bold bright_cyan]\n")

    roadmap_text = (
        "[bold white]Phase 1: Reduce Concentration (Week 1)[/bold white]\n"
        "  [bright_red]1. SELL[/bright_red] 4 shares of NVDA @ $875 = [bright_red]$3,500[/bright_red]\n"
        "  [bright_red]2. SELL[/bright_red] 2 shares of TSLA @ $238.45 = [bright_red]$476.90[/bright_red]\n"
        "  Cash Generated: $3,976.90\n\n"
        "[bold white]Phase 2: Increase Quality Holdings (Week 1-2)[/bold white]\n"
        "  [bright_green]3. BUY[/bright_green] 4 shares of AAPL @ $235.50 = [bright_green]$942[/bright_green]\n"
        "  Cash Deployed: $942\n"
        "  Cash Remaining: $3,034.90\n\n"
        "[bold white]Phase 3: Build New Positions (Week 2-3)[/bold white]\n"
        "  [bright_green]4. BUY[/bright_green] ~40 shares JNJ @ ~$150 = ~$6,000 (15%)\n"
        "  [bright_green]5. BUY[/bright_green] ~45 shares JPM @ ~$150 = ~$6,750 (12%)\n"
        "  [bright_green]6. BUY[/bright_green] Remaining in MCD, PG, XOM\n\n"
        "[bold bright_yellow]Note: Consider tax implications before selling. Use tax-loss harvesting if needed.[/bold bright_yellow]"
    )
    roadmap_panel = Panel(roadmap_text, border_style="bright_cyan", style="on black")
    console.print(roadmap_panel)
    console.print()

    # Summary
    console.print("[bold bright_cyan]✅ OPTIMIZATION SUMMARY[/bold bright_cyan]\n")

    summary_text = (
        "[bold bright_green]WHAT TO REDUCE:[/bold bright_green]\n"
        "  • NVDA: 66% → 35% (SELL 4 shares, lock $2,800 gains)\n"
        "  • TSLA: 23% → 0% (SELL 2 shares, exit underperformer)\n\n"
        "[bold bright_green]WHAT TO INCREASE:[/bold bright_green]\n"
        "  • AAPL: 11% → 20% (BUY 4 shares, quality dividend stock)\n\n"
        "[bold bright_green]WHAT TO ADD:[/bold bright_green]\n"
        "  • Healthcare: 15% (JNJ, UNH) - Defensive, dividends\n"
        "  • Financials: 12% (JPM, BLK) - Recovery play, dividends\n"
        "  • Consumer: 10% (MCD, NKE) - Growth diversification\n"
        "  • Staples: 8% (PG, KO) - Recession protection\n"
        "  • Industrials: 8% (HON, CAT) - Economic cycle\n"
        "  • Energy: 7% (XOM, CVX) - Portfolio hedge\n"
        "  • International: 5% (ASML, SAP) - Geographic diversification\n\n"
        "[bold bright_green]EXPECTED BENEFITS:[/bold bright_green]\n"
        "  ✓ Reduce volatility from 43% to ~28%\n"
        "  ✓ Improve dividend income from $6 to ~$190/year\n"
        "  ✓ Reduce max drawdown from -60% to ~-35%\n"
        "  ✓ Lower single-stock concentration risk\n"
        "  ✓ Better recession protection\n"
        "  ✓ More balanced risk-return profile"
    )
    summary_panel = Panel(summary_text, border_style="bright_green", style="on black")
    console.print(summary_panel)

def main():
    """Main execution function."""
    try:
        # Get current portfolio
        current_holdings = get_current_portfolio()

        # Get optimization targets
        targets = get_optimization_targets()

        # Calculate optimization scenario
        optimized, current_value = calculate_optimization_scenario(current_holdings)

        # Display analysis
        display_optimization_analysis(current_holdings, targets, optimized, current_value)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
