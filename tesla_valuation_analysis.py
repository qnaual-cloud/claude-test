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
    """Display comprehensive valuation analysis."""

    # Header
    title = Text("TESLA VALUATION ANALYSIS - THREE METHODS", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Current Valuation
    current_price = financials['current_price']
    current_color = "bright_yellow"

    current_text = (
        f"[bold white]Company:[/bold white] [bright_cyan]Tesla Inc. (TSLA)[/bright_cyan]\n"
        f"[bold white]Current Price:[/bold white] [{current_color}]${current_price:.2f}[/{current_color}]\n"
        f"[bold white]Market Cap:[/bold white] [bright_cyan]${financials['market_cap']:.1f}B[/bright_cyan]\n"
        f"[bold white]Analysis Date:[/bold white] [bright_white]{datetime.now().strftime('%B %d, %Y')}[/bright_white]"
    )
    current_panel = Panel(current_text, border_style="cyan", style="on black")
    console.print(current_panel)
    console.print()

    # METHOD 1: DCF ANALYSIS
    console.print("[bold bright_cyan]METHOD 1: DCF (Discounted Cash Flow) VALUATION[/bold bright_cyan]\n")

    dcf_value = dcf_data['intrinsic_value']
    dcf_diff = ((dcf_value - current_price) / current_price) * 100
    dcf_color = get_value_color(current_price, dcf_value)

    dcf_text = (
        f"[bold white]Intrinsic Value (DCF):[/bold white] [{dcf_color}]${dcf_value:.2f}[/{dcf_color}]\n"
        f"[bold white]Current Price:[/bold white] [bright_yellow]${current_price:.2f}[/bright_yellow]\n"
        f"[bold white]Upside/Downside:[/bold white] [{dcf_color}]{dcf_diff:+.1f}%[/{dcf_color}]\n"
        f"[bold white]Enterprise Value:[/bold white] [bright_cyan]${dcf_data['enterprise_value']:.1f}B[/bright_cyan]\n"
        f"[bold white]Discount Rate (WACC):[/bold white] [bright_cyan]{dcf_data['discount_rate']*100:.1f}%[/bright_cyan]\n"
        f"[bold white]Terminal Growth:[/bold white] [bright_cyan]{dcf_data['terminal_growth']*100:.1f}%[/bright_cyan]\n"
        f"[dim]DCF assumes 5-year cash flow projection with declining growth rates[/dim]"
    )
    dcf_panel = Panel(dcf_text, border_style="bright_cyan", style="on black")
    console.print(dcf_panel)
    console.print()

    # METHOD 2: P/E MULTIPLE
    console.print("[bold bright_cyan]METHOD 2: P/E MULTIPLE VALUATION[/bold bright_cyan]\n")

    pe_value = pe_data['consensus_value']
    pe_diff = ((pe_value - current_price) / current_price) * 100
    pe_color = get_value_color(current_price, pe_value)

    pe_text = (
        f"[bold white]Fair Value (P/E Multiple):[/bold white] [{pe_color}]${pe_value:.2f}[/{pe_color}]\n"
        f"[bold white]Current Price:[/bold white] [bright_yellow]${current_price:.2f}[/bright_yellow]\n"
        f"[bold white]Upside/Downside:[/bold white] [{pe_color}]{pe_diff:+.1f}%[/{pe_color}]\n"
        f"[bold white]Current P/E Ratio:[/bold white] [bright_yellow]{financials['current_pe']:.1f}x[/bright_yellow]\n"
        f"[bold white]Fair Value P/E:[/bold white] [bright_cyan]{pe_data['consensus_pe']:.1f}x[/bright_cyan]\n"
        f"[bold white]EPS:[/bold white] [bright_cyan]${pe_data['eps']:.2f}[/bright_cyan]\n\n"
        f"[dim]Conservative (Auto Maker): {pe_data['auto_maker_pe']:.1f}x P/E = ${pe_data['auto_maker_value']:.2f}[/dim]\n"
        f"[dim]Optimistic (Tech Growth): {pe_data['tech_growth_pe']:.1f}x P/E = ${pe_data['tech_growth_value']:.2f}[/dim]"
    )
    pe_panel = Panel(pe_text, border_style="bright_cyan", style="on black")
    console.print(pe_panel)
    console.print()

    # METHOD 3: PRICE-TO-BOOK
    console.print("[bold bright_cyan]METHOD 3: PRICE-TO-BOOK VALUATION[/bold bright_cyan]\n")

    pb_value = pb_data['fair_value_value']
    pb_diff = ((pb_value - current_price) / current_price) * 100
    pb_color = get_value_color(current_price, pb_value)

    pb_text = (
        f"[bold white]Fair Value (P/B):[/bold white] [{pb_color}]${pb_value:.2f}[/{pb_color}]\n"
        f"[bold white]Current Price:[/bold white] [bright_yellow]${current_price:.2f}[/bright_yellow]\n"
        f"[bold white]Upside/Downside:[/bold white] [{pb_color}]{pb_diff:+.1f}%[/{pb_color}]\n"
        f"[bold white]Book Value per Share:[/bold white] [bright_cyan]${pb_data['book_value_per_share']:.2f}[/bright_cyan]\n"
        f"[bold white]Current P/B Ratio:[/bold white] [bright_yellow]{financials['current_pb']:.2f}x[/bright_yellow]\n"
        f"[bold white]Fair Value P/B:[/bold white] [bright_cyan]{pb_data['fair_value_pb']:.2f}x[/bright_cyan]\n\n"
        f"[dim]Conservative (2.5x P/B): ${pb_data['conservative_value']:.2f}[/dim]\n"
        f"[dim]Optimistic (4.5x P/B): ${pb_data['optimistic_value']:.2f}[/dim]"
    )
    pb_panel = Panel(pb_text, border_style="bright_cyan", style="on black")
    console.print(pb_panel)
    console.print()

    # VALUATION COMPARISON TABLE
    console.print("[bold bright_cyan]📊 VALUATION METHODS COMPARISON[/bold bright_cyan]\n")

    comparison_table = Table(show_header=True,
                            header_style="bold white on dark_blue",
                            border_style="cyan",
                            padding=(0, 1))

    comparison_table.add_column("Method", style="bold white")
    comparison_table.add_column("Fair Value", style="bright_white", justify="right")
    comparison_table.add_column("vs Current", style="bright_white", justify="right")
    comparison_table.add_column("Upside", style="bright_white", justify="right")
    comparison_table.add_column("Confidence", style="bright_white")

    dcf_color = get_value_color(current_price, dcf_value)
    pe_color = get_value_color(current_price, pe_value)
    pb_color = get_value_color(current_price, pb_value)

    comparison_table.add_row(
        "DCF Analysis",
        f"[{dcf_color}]${dcf_value:.2f}[/{dcf_color}]",
        f"[{dcf_color}]{dcf_diff:+.1f}%[/{dcf_color}]",
        "40%",
        "[bright_green]High[/bright_green]"
    )

    comparison_table.add_row(
        "P/E Multiple",
        f"[{pe_color}]${pe_value:.2f}[/{pe_color}]",
        f"[{pe_color}]{pe_diff:+.1f}%[/{pe_color}]",
        "35%",
        "[green]Medium[/green]"
    )

    comparison_table.add_row(
        "Price-to-Book",
        f"[{pb_color}]${pb_value:.2f}[/{pb_color}]",
        f"[{pb_color}]{pb_diff:+.1f}%[/{pb_color}]",
        "25%",
        "[yellow]Medium[/yellow]"
    )

    console.print(comparison_table)
    console.print()

    # CONSENSUS FAIR VALUE
    consensus_data = calculate_consensus_fair_value(dcf_value, pe_value, pb_value)
    consensus_value = consensus_data['weighted']
    consensus_diff = ((consensus_value - current_price) / current_price) * 100
    consensus_color = get_value_color(current_price, consensus_value)

    console.print("[bold bright_cyan]🎯 CONSENSUS FAIR VALUE[/bold bright_cyan]\n")

    consensus_text = (
        f"[bold bright_green]FAIR VALUE:[/bold bright_green] [{consensus_color}]${consensus_value:.2f}[/{consensus_color}]\n"
        f"[bold white]Current Price:[/bold white] [bright_yellow]${current_price:.2f}[/bright_yellow]\n"
        f"[bold white]Upside/Downside:[/bold white] [{consensus_color}]{consensus_diff:+.1f}%[/{consensus_color}]\n\n"
        f"[bold white]Weighting:[/bold white]\n"
        f"  • DCF Method: 40% = ${dcf_value * 0.40:.2f}\n"
        f"  • P/E Method: 35% = ${pe_value * 0.35:.2f}\n"
        f"  • P/B Method: 25% = ${pb_value * 0.25:.2f}\n\n"
        f"[bright_cyan]Equal-Weight Average: ${consensus_data['equal_weight']:.2f}[/bright_cyan]"
    )
    consensus_panel = Panel(consensus_text, border_style="bright_green", style="on black")
    console.print(consensus_panel)
    console.print()

    # VALUATION RANGE
    console.print("[bold bright_cyan]📈 VALUATION RANGE[/bold bright_cyan]\n")

    low_value = min(dcf_value, pe_data['auto_maker_value'], pb_data['conservative_value'])
    high_value = max(dcf_value, pe_data['tech_growth_value'], pb_data['optimistic_value'])

    range_text = (
        f"[bold white]Conservative Case:[/bold white] [bright_red]${low_value:.2f}[/bright_red]\n"
        f"[bold white]Base Case (Consensus):[/bold white] [bright_green]${consensus_value:.2f}[/bright_green]\n"
        f"[bold white]Optimistic Case:[/bold white] [bright_green]${high_value:.2f}[/bright_green]\n\n"
        f"[dim]Range: ${low_value:.2f} - ${high_value:.2f}[/dim]\n"
        f"[bold white]Current Price:[/bold white] [bright_yellow]${current_price:.2f}[/bright_yellow]"
    )
    range_panel = Panel(range_text, border_style="cyan", style="on black")
    console.print(range_panel)
    console.print()

    # INVESTMENT RECOMMENDATION
    console.print("[bold bright_cyan]💡 INVESTMENT RECOMMENDATION[/bold bright_cyan]\n")

    if consensus_diff > 15:
        recommendation = "[bold bright_green]STRONG BUY[/bold bright_green]"
        reason = f"Significant upside ({consensus_diff:.1f}%) to consensus fair value"
    elif consensus_diff > 5:
        recommendation = "[bold green]BUY[/bold green]"
        reason = f"Modest upside ({consensus_diff:.1f}%) suggests undervaluation"
    elif consensus_diff > -5:
        recommendation = "[bold yellow]HOLD[/bold yellow]"
        reason = f"Fair value within 5%, limited upside/downside"
    elif consensus_diff > -15:
        recommendation = "[bold bright_yellow]SELL[/bold bright_yellow]"
        reason = f"Modest overvaluation ({abs(consensus_diff):.1f}%)"
    else:
        recommendation = "[bold bright_red]STRONG SELL[/bold bright_red]"
        reason = f"Significant overvaluation ({abs(consensus_diff):.1f}%)"

    rec_text = (
        f"[bold white]Rating:[/bold white] {recommendation}\n"
        f"[bold white]Rationale:[/bold white] {reason}\n\n"
        f"[dim]Based on consensus fair value of ${consensus_value:.2f} vs current price ${current_price:.2f}[/dim]"
    )
    rec_panel = Panel(rec_text, border_style="cyan", style="on black")
    console.print(rec_panel)
    console.print()

    # KEY ASSUMPTIONS
    console.print("[bold bright_cyan]📋 KEY ASSUMPTIONS[/bold bright_cyan]\n")

    assumptions_text = (
        "[bold white]DCF Model:[/bold white]\n"
        "  • 5-year cash flow projection with declining growth (15% → 8%)\n"
        "  • Terminal growth rate: 3%\n"
        "  • Discount rate (WACC): 9%\n\n"
        "[bold white]P/E Method:[/bold white]\n"
        "  • Consensus fair P/E: 22x (blend of auto maker and tech)\n"
        "  • Current P/E: 16.2x\n"
        "  • EPS basis: $14.7B net income / 3.179B shares\n\n"
        "[bold white]P/B Method:[/bold white]\n"
        "  • Fair value P/B: 3.5x (blend of asset/growth valuations)\n"
        "  • Book value: $165B equity / 3.179B shares\n"
        "  • Range: 2.5x (conservative) to 4.5x (optimistic)"
    )
    assumptions_panel = Panel(assumptions_text, border_style="cyan", style="on black")
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
