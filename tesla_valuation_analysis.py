#!/usr/bin/env python3
"""
Tesla Valuation Analysis - Three Methods
DCF, P/E Multiple, and Price-to-Book valuations with consensus analysis.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_tesla_financials():
    """Get Tesla's financial data for valuation."""
    print("Loading Tesla financial data...\n")

    financials = {
        'ticker': 'TSLA',
        'company': 'Tesla Inc.',
        'current_price': 238.45,
        'shares_outstanding': 3.179,  # Billion shares
        'market_cap': 758.41,  # Billion

        # Latest financial data (FY2024)
        'revenue': 96.773,  # $96.773B annual
        'net_income': 14.724,  # $14.724B annual
        'fcf': 13.256,  # $13.256B free cash flow
        'total_assets': 346.000,  # $346B
        'total_equity': 165.000,  # $165B
        'book_value': 51.85,  # Book value per share

        # Growth metrics
        'revenue_growth': 0.0206,  # 2% YoY
        'earnings_growth': 0.15,  # 15% estimated next 3 years

        # Multiples
        'current_pe': 16.2,  # Current P/E ratio
        'current_pb': 4.60,  # Current Price-to-Book
        'current_ps': 7.84,  # Price-to-Sales
    }

    return financials

def calculate_dcf_valuation(financials):
    """Calculate DCF intrinsic value."""

    current_fcf = financials['fcf']

    # Conservative growth assumptions for Tesla
    growth_rates = [0.15, 0.13, 0.12, 0.10, 0.08]  # Declining growth over 5 years
    terminal_growth = 0.03  # 3% perpetual growth
    discount_rate = 0.09   # 9% WACC

    # Project free cash flows
    projected_fcf = []
    fcf = current_fcf

    for growth in growth_rates:
        fcf = fcf * (1 + growth)
        projected_fcf.append(fcf)

    # Terminal value
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)

    # Discount to present value
    pv_fcf = []
    for i, fcf_value in enumerate(projected_fcf):
        pv = fcf_value / ((1 + discount_rate) ** (i + 1))
        pv_fcf.append(pv)

    pv_terminal = terminal_value / ((1 + discount_rate) ** 5)

    # Enterprise value
    enterprise_value = sum(pv_fcf) + pv_terminal

    # Equity value (subtract net debt)
    net_debt = 7.850 - 29.089  # Total debt - cash
    equity_value = enterprise_value - net_debt

    # Value per share
    intrinsic_value = equity_value / financials['shares_outstanding']

    dcf_data = {
        'intrinsic_value': intrinsic_value,
        'enterprise_value': enterprise_value,
        'equity_value': equity_value,
        'pv_fcf': sum(pv_fcf),
        'pv_terminal': pv_terminal,
        'terminal_growth': terminal_growth,
        'discount_rate': discount_rate,
    }

    return dcf_data

def calculate_pe_valuation(financials):
    """Calculate fair value using P/E multiple method."""

    # Industry P/E multiples (auto makers vs growth tech)
    # Tesla trades between premium auto maker (15-20 P/E) and growth tech (25-40 P/E)

    # Scenario 1: Premium Auto Maker valuation
    auto_pe = 18.0  # High-quality auto maker P/E

    # Scenario 2: Tech Growth valuation
    tech_pe = 28.0  # Growth tech company P/E

    # Scenario 3: Consensus valuation
    consensus_pe = 22.0  # Blended approach

    eps = financials['net_income'] / financials['shares_outstanding']

    pe_valuations = {
        'auto_maker_pe': auto_pe,
        'auto_maker_value': eps * auto_pe,
        'tech_growth_pe': tech_pe,
        'tech_growth_value': eps * tech_pe,
        'consensus_pe': consensus_pe,
        'consensus_value': eps * consensus_pe,
        'current_pe': financials['current_pe'],
        'eps': eps,
    }

    return pe_valuations

def calculate_pb_valuation(financials):
    """Calculate fair value using Price-to-Book method."""

    # P/B multiples for different scenarios
    # Auto makers typically trade 0.8-1.2 P/B
    # Growth companies can trade 3-6 P/B
    # Tesla blend: 2.5-4.5 P/B

    conservative_pb = 2.5  # Conservative valuation
    fair_value_pb = 3.5    # Fair value estimate
    optimistic_pb = 4.5    # Optimistic valuation

    book_value_per_share = financials['total_equity'] / financials['shares_outstanding']

    pb_valuations = {
        'book_value_per_share': book_value_per_share,
        'conservative_pb': conservative_pb,
        'conservative_value': book_value_per_share * conservative_pb,
        'fair_value_pb': fair_value_pb,
        'fair_value_value': book_value_per_share * fair_value_pb,
        'optimistic_pb': optimistic_pb,
        'optimistic_value': book_value_per_share * optimistic_pb,
        'current_pb': financials['current_pb'],
    }

    return pb_valuations

def calculate_consensus_fair_value(dcf_value, pe_value, pb_value):
    """Calculate consensus fair value from all three methods."""

    # Weight each method
    # DCF: 40% (most rigorous)
    # P/E: 35% (market-based)
    # P/B: 25% (asset-based)

    consensus = (dcf_value * 0.40) + (pe_value * 0.35) + (pb_value * 0.25)

    # Also calculate equal-weight for comparison
    equal_weight = (dcf_value + pe_value + pb_value) / 3

    return {
        'weighted': consensus,
        'equal_weight': equal_weight,
        'dcf_weight': 0.40,
        'pe_weight': 0.35,
        'pb_weight': 0.25,
    }

def get_value_color(current, fair_value):
    """Get color based on valuation gap."""
    diff_pct = ((fair_value - current) / current) * 100

    if diff_pct > 20:
        return 'bright_green'
    elif diff_pct > 10:
        return 'green'
    elif diff_pct > 0:
        return 'yellow'
    elif diff_pct > -10:
        return 'bright_yellow'
    elif diff_pct > -20:
        return 'bright_red'
    else:
        return 'bold bright_red'

def display_valuation_analysis(financials, dcf_data, pe_data, pb_data):
    """Display comprehensive valuation analysis with vibrant highlighting."""

    # Header
    title = Text("TESLA VALUATION ANALYSIS - THREE METHODS", style="bold bright_magenta on black")
    console.print(Align.center(title))
    console.print()

    # Current Valuation
    current_price = financials['current_price']
    current_color = "bold bright_yellow"

    current_text = (
        f"[bold bright_white]Company:[/bold bright_white] [bold bright_cyan]Tesla Inc. (TSLA)[/bold bright_cyan]\n"
        f"[bold bright_white]Current Price:[/bold bright_white] [{current_color}]${current_price:.2f}[/{current_color}]\n"
        f"[bold bright_white]Market Cap:[/bold bright_white] [bold bright_cyan]${financials['market_cap']:.1f}B[/bold bright_cyan]\n"
        f"[bold bright_white]Analysis Date:[/bold bright_white] [bold bright_white]{datetime.now().strftime('%B %d, %Y')}[/bold bright_white]"
    )
    current_panel = Panel(current_text, border_style="bright_magenta", style="on black")
    console.print(current_panel)
    console.print()

    # METHOD 1: DCF ANALYSIS
    console.print("[bold bright_magenta]⭐ METHOD 1: DCF (Discounted Cash Flow) VALUATION[/bold bright_magenta]\n")

    dcf_value = dcf_data['intrinsic_value']
    dcf_diff = ((dcf_value - current_price) / current_price) * 100
    dcf_color = get_value_color(current_price, dcf_value)

    dcf_text = (
        f"[bold bright_white]Intrinsic Value (DCF):[/bold bright_white] [{dcf_color}]${dcf_value:.2f}[/{dcf_color}]\n"
        f"[bold bright_white]Current Price:[/bold bright_white] [{current_color}]${current_price:.2f}[/{current_color}]\n"
        f"[bold bright_white]Upside/Downside:[/bold bright_white] [{dcf_color}]{dcf_diff:+.1f}%[/{dcf_color}]\n"
        f"[bold bright_white]Enterprise Value:[/bold bright_white] [bold bright_green]${dcf_data['enterprise_value']:.1f}B[/bold bright_green]\n"
        f"[bold bright_white]Discount Rate (WACC):[/bold bright_white] [bold bright_cyan]{dcf_data['discount_rate']*100:.1f}%[/bold bright_cyan]\n"
        f"[bold bright_white]Terminal Growth:[/bold bright_white] [bold bright_cyan]{dcf_data['terminal_growth']*100:.1f}%[/bold bright_cyan]\n"
        f"[bold white]DCF assumes 5-year cash flow projection with declining growth rates[/bold white]"
    )
    dcf_panel = Panel(dcf_text, border_style="bright_magenta", style="on black")
    console.print(dcf_panel)
    console.print()

    # METHOD 2: P/E MULTIPLE
    console.print("[bold bright_magenta]⭐ METHOD 2: P/E MULTIPLE VALUATION[/bold bright_magenta]\n")

    pe_value = pe_data['consensus_value']
    pe_diff = ((pe_value - current_price) / current_price) * 100
    pe_color = get_value_color(current_price, pe_value)

    pe_text = (
        f"[bold bright_white]Fair Value (P/E Multiple):[/bold bright_white] [{pe_color}]${pe_value:.2f}[/{pe_color}]\n"
        f"[bold bright_white]Current Price:[/bold bright_white] [{current_color}]${current_price:.2f}[/{current_color}]\n"
        f"[bold bright_white]Upside/Downside:[/bold bright_white] [{pe_color}]{pe_diff:+.1f}%[/{pe_color}]\n"
        f"[bold bright_white]Current P/E Ratio:[/bold bright_white] [{current_color}]{financials['current_pe']:.1f}x[/{current_color}]\n"
        f"[bold bright_white]Fair Value P/E:[/bold bright_white] [bold bright_cyan]{pe_data['consensus_pe']:.1f}x[/bold bright_cyan]\n"
        f"[bold bright_white]EPS:[/bold bright_white] [bold bright_green]${pe_data['eps']:.2f}[/bold bright_green]\n\n"
        f"[bold white]Conservative (Auto Maker): {pe_data['auto_maker_pe']:.1f}x P/E = [bold bright_red]${pe_data['auto_maker_value']:.2f}[/bold bright_red][/bold white]\n"
        f"[bold white]Optimistic (Tech Growth): {pe_data['tech_growth_pe']:.1f}x P/E = [bold bright_green]${pe_data['tech_growth_value']:.2f}[/bold bright_green][/bold white]"
    )
    pe_panel = Panel(pe_text, border_style="bright_magenta", style="on black")
    console.print(pe_panel)
    console.print()

    # METHOD 3: PRICE-TO-BOOK
    console.print("[bold bright_magenta]⭐ METHOD 3: PRICE-TO-BOOK VALUATION[/bold bright_magenta]\n")

    pb_value = pb_data['fair_value_value']
    pb_diff = ((pb_value - current_price) / current_price) * 100
    pb_color = get_value_color(current_price, pb_value)

    pb_text = (
        f"[bold bright_white]Fair Value (P/B):[/bold bright_white] [{pb_color}]${pb_value:.2f}[/{pb_color}]\n"
        f"[bold bright_white]Current Price:[/bold bright_white] [{current_color}]${current_price:.2f}[/{current_color}]\n"
        f"[bold bright_white]Upside/Downside:[/bold bright_white] [{pb_color}]{pb_diff:+.1f}%[/{pb_color}]\n"
        f"[bold bright_white]Book Value per Share:[/bold bright_white] [bold bright_cyan]${pb_data['book_value_per_share']:.2f}[/bold bright_cyan]\n"
        f"[bold bright_white]Current P/B Ratio:[/bold bright_white] [{current_color}]{financials['current_pb']:.2f}x[/{current_color}]\n"
        f"[bold bright_white]Fair Value P/B:[/bold bright_white] [bold bright_cyan]{pb_data['fair_value_pb']:.2f}x[/bold bright_cyan]\n\n"
        f"[bold white]Conservative (2.5x P/B): [bold bright_red]${pb_data['conservative_value']:.2f}[/bold bright_red][/bold white]\n"
        f"[bold white]Optimistic (4.5x P/B): [bold bright_green]${pb_data['optimistic_value']:.2f}[/bold bright_green][/bold white]"
    )
    pb_panel = Panel(pb_text, border_style="bright_magenta", style="on black")
    console.print(pb_panel)
    console.print()

    # VALUATION COMPARISON TABLE
    console.print("[bold bright_magenta]📊 VALUATION METHODS COMPARISON[/bold bright_magenta]\n")

    comparison_table = Table(show_header=True,
                            header_style="bold white on bright_magenta",
                            border_style="bright_magenta",
                            padding=(0, 1))

    comparison_table.add_column("Method", style="bold bright_white")
    comparison_table.add_column("Fair Value", style="bold bright_white", justify="right")
    comparison_table.add_column("vs Current", style="bold bright_white", justify="right")
    comparison_table.add_column("Upside", style="bold bright_white", justify="right")
    comparison_table.add_column("Confidence", style="bold bright_white")

    dcf_color = get_value_color(current_price, dcf_value)
    pe_color = get_value_color(current_price, pe_value)
    pb_color = get_value_color(current_price, pb_value)

    comparison_table.add_row(
        "[bold bright_green]DCF Analysis[/bold bright_green]",
        f"[bold {dcf_color}]${dcf_value:.2f}[/bold {dcf_color}]",
        f"[bold {dcf_color}]{dcf_diff:+.1f}%[/bold {dcf_color}]",
        "[bold bright_green]40%[/bold bright_green]",
        "[bold bright_green]★★★ High[/bold bright_green]"
    )

    comparison_table.add_row(
        "[bold bright_yellow]P/E Multiple[/bold bright_yellow]",
        f"[bold {pe_color}]${pe_value:.2f}[/bold {pe_color}]",
        f"[bold {pe_color}]{pe_diff:+.1f}%[/bold {pe_color}]",
        "[bold bright_yellow]35%[/bold bright_yellow]",
        "[bold yellow]★★ Medium[/bold yellow]"
    )

    comparison_table.add_row(
        "[bold bright_cyan]Price-to-Book[/bold bright_cyan]",
        f"[bold {pb_color}]${pb_value:.2f}[/bold {pb_color}]",
        f"[bold {pb_color}]{pb_diff:+.1f}%[/bold {pb_color}]",
        "[bold bright_cyan]25%[/bold bright_cyan]",
        "[bold bright_cyan]★★ Medium[/bold bright_cyan]"
    )

    console.print(comparison_table)
    console.print()

    # CONSENSUS FAIR VALUE
    consensus_data = calculate_consensus_fair_value(dcf_value, pe_value, pb_value)
    consensus_value = consensus_data['weighted']
    consensus_diff = ((consensus_value - current_price) / current_price) * 100
    consensus_color = get_value_color(current_price, consensus_value)

    console.print("[bold bright_magenta]🎯 CONSENSUS FAIR VALUE[/bold bright_magenta]\n")

    consensus_text = (
        f"[bold bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold bright_magenta]\n"
        f"[bold bright_green]FAIR VALUE:[/bold bright_green] [bold {consensus_color}]${consensus_value:.2f}[/bold {consensus_color}]\n"
        f"[bold bright_white]Current Price:[/bold bright_white] [{current_color}]${current_price:.2f}[/{current_color}]\n"
        f"[bold bright_white]Upside/Downside:[/bold bright_white] [bold {consensus_color}]{consensus_diff:+.1f}%[/bold {consensus_color}]\n"
        f"[bold bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold bright_magenta]\n"
        f"[bold bright_white]Weighting:[/bold bright_white]\n"
        f"  [bold bright_green]•[/bold bright_green] DCF Method: [bold bright_green]40%[/bold bright_green] = [bold bright_green]${dcf_value * 0.40:.2f}[/bold bright_green]\n"
        f"  [bold bright_yellow]•[/bold bright_yellow] P/E Method: [bold bright_yellow]35%[/bold bright_yellow] = [bold bright_yellow]${pe_value * 0.35:.2f}[/bold bright_yellow]\n"
        f"  [bold bright_cyan]•[/bold bright_cyan] P/B Method: [bold bright_cyan]25%[/bold bright_cyan] = [bold bright_cyan]${pb_value * 0.25:.2f}[/bold bright_cyan]\n\n"
        f"[bold bright_magenta]Equal-Weight Average:[/bold bright_magenta] [bold bright_magenta]${consensus_data['equal_weight']:.2f}[/bold bright_magenta]"
    )
    consensus_panel = Panel(consensus_text, border_style="bold bright_magenta", style="on black")
    console.print(consensus_panel)
    console.print()

    # VALUATION RANGE
    console.print("[bold bright_magenta]📈 VALUATION RANGE[/bold bright_magenta]\n")

    low_value = min(dcf_value, pe_data['auto_maker_value'], pb_data['conservative_value'])
    high_value = max(dcf_value, pe_data['tech_growth_value'], pb_data['optimistic_value'])

    range_text = (
        f"[bold bright_white]Conservative Case:[/bold bright_white] [bold bright_red]${low_value:.2f}[/bold bright_red]  [bright_red]▼▼▼[/bright_red]\n"
        f"[bold bright_white]Base Case (Consensus):[/bold bright_white] [bold bright_magenta]${consensus_value:.2f}[/bold bright_magenta]  [bright_magenta]━━━[/bright_magenta]\n"
        f"[bold bright_white]Optimistic Case:[/bold bright_white] [bold bright_green]${high_value:.2f}[/bold bright_green]  [bright_green]▲▲▲[/bright_green]\n\n"
        f"[bold white]Range:[/bold white] [bold bright_red]${low_value:.2f}[/bold bright_red] → [bold bright_green]${high_value:.2f}[/bold bright_green]\n"
        f"[bold bright_white]Current Price:[/bold bright_white] [{current_color}]${current_price:.2f}[/{current_color}]"
    )
    range_panel = Panel(range_text, border_style="bright_magenta", style="on black")
    console.print(range_panel)
    console.print()

    # INVESTMENT RECOMMENDATION
    console.print("[bold bright_magenta]💡 INVESTMENT RECOMMENDATION[/bold bright_magenta]\n")

    if consensus_diff > 15:
        recommendation = "[bold bright_green]🟢 STRONG BUY[/bold bright_green]"
        reason = f"Significant upside ({consensus_diff:.1f}%) to consensus fair value"
    elif consensus_diff > 5:
        recommendation = "[bold bright_green]🟢 BUY[/bold bright_green]"
        reason = f"Modest upside ({consensus_diff:.1f}%) suggests undervaluation"
    elif consensus_diff > -5:
        recommendation = "[bold bright_yellow]🟡 HOLD[/bold bright_yellow]"
        reason = f"Fair value within 5%, limited upside/downside"
    elif consensus_diff > -15:
        recommendation = "[bold bright_red]🔴 SELL[/bold bright_red]"
        reason = f"Modest overvaluation ({abs(consensus_diff):.1f}%)"
    else:
        recommendation = "[bold bright_red]🔴 STRONG SELL[/bold bright_red]"
        reason = f"Significant overvaluation ({abs(consensus_diff):.1f}%)"

    rec_text = (
        f"[bold bright_white]Rating:[/bold bright_white] {recommendation}\n"
        f"[bold bright_white]Rationale:[/bold bright_white] {reason}\n\n"
        f"[bold white]Based on consensus fair value of [bold bright_magenta]${consensus_value:.2f}[/bold bright_magenta] vs current price [{current_color}]${current_price:.2f}[/{current_color}][/bold white]"
    )
    rec_panel = Panel(rec_text, border_style="bold bright_red", style="on black")
    console.print(rec_panel)
    console.print()

    # KEY ASSUMPTIONS
    console.print("[bold bright_magenta]📋 KEY ASSUMPTIONS[/bold bright_magenta]\n")

    assumptions_text = (
        "[bold bright_white]DCF Model:[/bold bright_white]\n"
        "  [bright_green]✓[/bright_green] 5-year cash flow projection with declining growth (15% → 8%)\n"
        "  [bright_green]✓[/bright_green] Terminal growth rate: 3%\n"
        "  [bright_green]✓[/bright_green] Discount rate (WACC): 9%\n\n"
        "[bold bright_white]P/E Method:[/bold bright_white]\n"
        "  [bright_yellow]✓[/bright_yellow] Consensus fair P/E: 22x (blend of auto maker and tech)\n"
        "  [bright_yellow]✓[/bright_yellow] Current P/E: 16.2x\n"
        "  [bright_yellow]✓[/bright_yellow] EPS basis: $14.7B net income / 3.179B shares\n\n"
        "[bold bright_white]P/B Method:[/bold bright_white]\n"
        "  [bright_cyan]✓[/bright_cyan] Fair value P/B: 3.5x (blend of asset/growth valuations)\n"
        "  [bright_cyan]✓[/bright_cyan] Book value: $165B equity / 3.179B shares\n"
        "  [bright_cyan]✓[/bright_cyan] Range: 2.5x (conservative) to 4.5x (optimistic)"
    )
    assumptions_panel = Panel(assumptions_text, border_style="bright_magenta", style="on black")
    console.print(assumptions_panel)

def main():
    """Main execution function."""
    try:
        # Get financials
        financials = get_tesla_financials()

        # Calculate valuations using three methods
        dcf_data = calculate_dcf_valuation(financials)
        pe_data = calculate_pe_valuation(financials)
        pb_data = calculate_pb_valuation(financials)

        # Display analysis
        display_valuation_analysis(financials, dcf_data, pe_data, pb_data)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
