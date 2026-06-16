#!/usr/bin/env python3
"""
DCF Stock Valuation Analysis - Tesla
Calculates intrinsic value using Discounted Cash Flow analysis.
Compares intrinsic value to current stock price.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_tesla_financials():
    """Get Tesla's current financial data."""
    print("Loading Tesla financial data...")

    # Tesla FY2024 actual financials (in billions, except ratios)
    financials = {
        'ticker': 'TSLA',
        'company_name': 'Tesla Inc.',
        'current_price': 238.45,  # Approximate current price
        'shares_outstanding': 3.179,  # Billion shares
        'annual_revenue': 96.773,  # FY2024: $96.773B
        'free_cash_flow': 13.256,  # FY2024: $13.256B
        'net_income': 14.724,  # FY2024: $14.724B
        'total_debt': 7.850,  # Approximate
        'cash': 29.089,  # FY2024
    }

    return financials

def calculate_dcf_valuation(financials):
    """Calculate DCF intrinsic value for Tesla."""

    # DCF Parameters
    current_fcf = financials['free_cash_flow']

    # Growth assumptions for Tesla
    # Year 1-5: Declining growth rates (Tesla maturing)
    growth_rates = [0.25, 0.20, 0.18, 0.15, 0.12]  # 25%, 20%, 18%, 15%, 12%
    terminal_growth = 0.03  # 3% perpetual growth (GDP growth rate)
    discount_rate = 0.09  # 9% WACC (Weighted Average Cost of Capital)

    # Project free cash flows for 5 years
    projected_fcf = []
    fcf = current_fcf

    for growth in growth_rates:
        fcf = fcf * (1 + growth)
        projected_fcf.append(fcf)

    # Calculate terminal value (Year 5 FCF growing at perpetual rate)
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)

    # Discount cash flows and terminal value to present value
    pv_fcf = []
    for i, fcf_value in enumerate(projected_fcf):
        pv = fcf_value / ((1 + discount_rate) ** (i + 1))
        pv_fcf.append(pv)

    # Discount terminal value
    pv_terminal = terminal_value / ((1 + discount_rate) ** 5)

    # Calculate enterprise value
    enterprise_value = sum(pv_fcf) + pv_terminal

    # Calculate equity value (Enterprise Value - Net Debt)
    net_debt = financials['total_debt'] - financials['cash']
    equity_value = enterprise_value - net_debt

    # Calculate intrinsic value per share
    intrinsic_value_per_share = equity_value / financials['shares_outstanding']

    dcf_results = {
        'current_fcf': current_fcf,
        'projected_fcf': projected_fcf,
        'growth_rates': growth_rates,
        'terminal_growth': terminal_growth,
        'discount_rate': discount_rate,
        'terminal_fcf': terminal_fcf,
        'terminal_value': terminal_value,
        'pv_fcf': pv_fcf,
        'pv_terminal': pv_terminal,
        'enterprise_value': enterprise_value,
        'net_debt': net_debt,
        'equity_value': equity_value,
        'intrinsic_value_per_share': intrinsic_value_per_share,
    }

    return dcf_results

def calculate_valuation_score(current_price, intrinsic_value):
    """
    Score the stock 1-10 based on valuation.
    1 = Massively overvalued
    10 = Massively undervalued
    """
    price_to_intrinsic = current_price / intrinsic_value

    # Scoring logic
    if price_to_intrinsic < 0.5:
        return 10  # 50%+ undervalued
    elif price_to_intrinsic < 0.67:
        return 9   # 33-50% undervalued
    elif price_to_intrinsic < 0.80:
        return 8   # 20-33% undervalued
    elif price_to_intrinsic < 0.90:
        return 7   # 10-20% undervalued
    elif price_to_intrinsic < 1.0:
        return 6   # 0-10% undervalued
    elif price_to_intrinsic < 1.10:
        return 5   # 0-10% overvalued (fair value)
    elif price_to_intrinsic < 1.20:
        return 4   # 10-20% overvalued
    elif price_to_intrinsic < 1.33:
        return 3   # 20-33% overvalued
    elif price_to_intrinsic < 1.50:
        return 2   # 33-50% overvalued
    else:
        return 1   # 50%+ overvalued

def get_valuation_status(current_price, intrinsic_value):
    """Determine if stock is undervalued or overvalued."""
    if current_price < intrinsic_value:
        diff = ((intrinsic_value - current_price) / current_price) * 100
        return f"UNDERVALUED by {diff:.1f}%", "bright_green"
    else:
        diff = ((current_price - intrinsic_value) / intrinsic_value) * 100
        return f"OVERVALUED by {diff:.1f}%", "bright_red"

def get_score_color(score):
    """Get color based on valuation score."""
    if score >= 9:
        return "bright_green"
    elif score >= 8:
        return "green"
    elif score >= 7:
        return "cyan"
    elif score >= 6:
        return "yellow"
    elif score >= 5:
        return "yellow"
    elif score >= 4:
        return "bright_yellow"
    elif score >= 3:
        return "bright_red"
    else:
        return "bold bright_red"

def display_dcf_analysis(financials, dcf_results):
    """Display comprehensive DCF analysis with Rich formatting."""

    current_price = financials['current_price']
    intrinsic_value = dcf_results['intrinsic_value_per_share']

    # Header
    title = Text("DCF STOCK VALUATION ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Company Info
    info_text = (f"[bold white]Company:[/bold white] [bright_cyan]{financials['company_name']}[/bright_cyan]  "
                f"[bold white]Ticker:[/bold white] [bright_yellow]{financials['ticker']}[/bright_yellow]  "
                f"[bold white]Current Price:[/bold white] [bright_green]${current_price:.2f}[/bright_green]  "
                f"[bold white]Date:[/bold white] [bright_white]{datetime.now().strftime('%Y-%m-%d')}[/bright_white]")
    console.print(info_text)
    console.print()

    # Valuation Score Panel
    valuation_status, status_color = get_valuation_status(current_price, intrinsic_value)
    score = calculate_valuation_score(current_price, intrinsic_value)
    score_color = get_score_color(score)

    valuation_panel_text = (f"[{score_color}]INTRINSIC VALUE: ${intrinsic_value:.2f}/share[/{score_color}]\n"
                           f"[{score_color}]VALUATION SCORE: {score}/10[/{score_color}]\n"
                           f"[{status_color}]{valuation_status}[/{status_color}]")
    valuation_panel = Panel(valuation_panel_text, border_style="cyan", style="on black")
    console.print(valuation_panel)
    console.print()

    # Input Assumptions Table
    assumptions_table = Table(title="[bold cyan]DCF ASSUMPTIONS[/bold cyan]",
                             show_header=True,
                             header_style="bold white on dark_blue",
                             border_style="cyan",
                             padding=(0, 1))

    assumptions_table.add_column("Parameter", style="bold white")
    assumptions_table.add_column("Value", style="bright_white")

    assumptions_table.add_row("Current Free Cash Flow", f"[bright_yellow]${dcf_results['current_fcf']:.2f}B[/bright_yellow]")
    assumptions_table.add_row("Discount Rate (WACC)", f"[bright_yellow]{dcf_results['discount_rate']*100:.1f}%[/bright_yellow]")
    assumptions_table.add_row("Terminal Growth Rate", f"[bright_yellow]{dcf_results['terminal_growth']*100:.1f}%[/bright_yellow]")
    assumptions_table.add_row("Shares Outstanding", f"[bright_yellow]{financials['shares_outstanding']:.3f}B[/bright_yellow]")
    assumptions_table.add_row("Net Debt", f"[bright_yellow]${dcf_results['net_debt']:.2f}B[/bright_yellow]")

    console.print(assumptions_table)
    console.print()

    # 5-Year Cash Flow Projections
    fcf_table = Table(title="[bold cyan]5-YEAR CASH FLOW PROJECTIONS[/bold cyan]",
                     show_header=True,
                     header_style="bold white on dark_blue",
                     border_style="cyan",
                     padding=(0, 1))

    fcf_table.add_column("Year", style="bold white")
    fcf_table.add_column("Growth Rate", style="bright_white")
    fcf_table.add_column("Projected FCF ($B)", style="bright_white")
    fcf_table.add_column("Present Value ($B)", style="bright_white")

    for i, (fcf, growth, pv) in enumerate(zip(dcf_results['projected_fcf'],
                                               dcf_results['growth_rates'],
                                               dcf_results['pv_fcf']), 1):
        fcf_table.add_row(
            f"Year {i}",
            f"[bright_green]+{growth*100:.0f}%[/bright_green]",
            f"[bright_yellow]${fcf:.2f}B[/bright_yellow]",
            f"[bright_cyan]${pv:.2f}B[/bright_cyan]"
        )

    console.print(fcf_table)
    console.print()

    # DCF Components Breakdown
    components_table = Table(title="[bold cyan]DCF VALUATION COMPONENTS[/bold cyan]",
                            show_header=True,
                            header_style="bold white on dark_blue",
                            border_style="cyan",
                            padding=(0, 1))

    components_table.add_column("Component", style="bold white")
    components_table.add_column("Value ($B)", style="bright_white")
    components_table.add_column("% of Total", style="bright_white")

    pv_fcf_sum = sum(dcf_results['pv_fcf'])
    total_ev = dcf_results['enterprise_value']

    components_table.add_row(
        "PV of 5-Year FCF",
        f"[bright_green]${pv_fcf_sum:.2f}B[/bright_green]",
        f"[bright_green]{(pv_fcf_sum/total_ev)*100:.1f}%[/bright_green]"
    )
    components_table.add_row(
        "PV of Terminal Value",
        f"[bright_green]${dcf_results['pv_terminal']:.2f}B[/bright_green]",
        f"[bright_green]{(dcf_results['pv_terminal']/total_ev)*100:.1f}%[/bright_green]"
    )
    components_table.add_row(
        "Enterprise Value",
        f"[bright_cyan]${total_ev:.2f}B[/bright_cyan]",
        f"[bright_cyan]100.0%[/bright_cyan]"
    )
    components_table.add_row(
        "Less: Net Debt",
        f"[bright_red]${dcf_results['net_debt']:.2f}B[/bright_red]",
        "-"
    )
    components_table.add_row(
        "Equity Value",
        f"[bright_yellow]${dcf_results['equity_value']:.2f}B[/bright_yellow]",
        "-"
    )
    components_table.add_row(
        "[bold]Intrinsic Value per Share[/bold]",
        f"[bold bright_yellow]${intrinsic_value:.2f}[/bold bright_yellow]",
        "-"
    )

    console.print(components_table)
    console.print()

    # Detailed Analysis
    analysis_title = Text("VALUATION ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(analysis_title))
    console.print()

    # Price comparison
    price_diff = current_price - intrinsic_value
    price_diff_pct = (price_diff / intrinsic_value) * 100

    console.print(f"[bold cyan]💰 VALUATION COMPARISON[/bold cyan]")
    console.print(f"  Current Stock Price:    [bright_yellow]${current_price:.2f}[/bright_yellow]")
    console.print(f"  DCF Intrinsic Value:    [bright_cyan]${intrinsic_value:.2f}[/bright_cyan]")

    if price_diff < 0:
        console.print(f"  Difference:             [bright_green]${abs(price_diff):.2f} ({abs(price_diff_pct):.1f}%) UNDERVALUED[/bright_green]")
    else:
        console.print(f"  Difference:             [bright_red]${price_diff:.2f} ({price_diff_pct:.1f}%) OVERVALUED[/bright_red]")
    console.print()

    # Margin of Safety
    if current_price < intrinsic_value:
        mos = ((intrinsic_value - current_price) / intrinsic_value) * 100
        console.print(f"[bold bright_green]📊 MARGIN OF SAFETY[/bold bright_green]")
        console.print(f"  Investment provides {mos:.1f}% margin of safety")
        console.print(f"  Stock can fall {mos:.1f}% before reaching intrinsic value")
    else:
        downside = ((intrinsic_value - current_price) / current_price) * 100
        console.print(f"[bold bright_red]⚠️ DOWNSIDE RISK[/bold bright_red]")
        console.print(f"  Stock is {abs(downside):.1f}% above intrinsic value")
        console.print(f"  Downside risk if market reprices to DCF value")
    console.print()

    # Growth assumptions analysis
    console.print(f"[bold cyan]📈 GROWTH ASSUMPTIONS[/bold cyan]")
    console.print(f"  Year 1 Growth Rate:     [bright_green]+{dcf_results['growth_rates'][0]*100:.0f}%[/bright_green]")
    console.print(f"  Year 5 Growth Rate:     [bright_yellow]+{dcf_results['growth_rates'][4]*100:.0f}%[/bright_yellow]")
    console.print(f"  Terminal Growth Rate:   [yellow]{dcf_results['terminal_growth']*100:.1f}%[/yellow] (perpetual)")
    console.print(f"  [dim]Declining growth rates reflect Tesla's maturation[/dim]")
    console.print()

    # Terminal Value Analysis
    terminal_pct = (dcf_results['pv_terminal'] / total_ev) * 100
    console.print(f"[bold cyan]🎯 TERMINAL VALUE ANALYSIS[/bold cyan]")
    console.print(f"  Terminal Value:         [bright_yellow]${dcf_results['terminal_value']:.2f}B[/bright_yellow]")
    console.print(f"  PV of Terminal Value:   [bright_yellow]${dcf_results['pv_terminal']:.2f}B[/bright_yellow]")
    console.print(f"  % of Enterprise Value:  [bright_yellow]{terminal_pct:.1f}%[/bright_yellow]")
    console.print()

    # Investment Recommendation
    if score >= 8:
        recommendation = "[bold bright_green]STRONG BUY[/bold bright_green]"
        reason = "Stock is significantly undervalued with strong upside potential"
    elif score >= 7:
        recommendation = "[bold green]BUY[/bold green]"
        reason = "Stock offers attractive valuation with reasonable upside"
    elif score >= 6:
        recommendation = "[bold cyan]HOLD[/bold cyan]"
        reason = "Stock is slightly undervalued; suitable for patient investors"
    elif score >= 5:
        recommendation = "[bold yellow]HOLD[/bold yellow]"
        reason = "Stock is fairly valued; limited margin of safety"
    elif score >= 4:
        recommendation = "[bold bright_yellow]SELL[/bold bright_yellow]"
        reason = "Stock is modestly overvalued; limited upside"
    elif score >= 3:
        recommendation = "[bold bright_red]STRONG SELL[/bold bright_red]"
        reason = "Stock is significantly overvalued; material downside risk"
    else:
        recommendation = "[bold bright_red]AVOID[/bold bright_red]"
        reason = "Stock is massively overvalued; significant downside risk"

    console.print(f"[bold cyan]🎯 INVESTMENT RECOMMENDATION[/bold cyan]")
    console.print(f"  Recommendation:         {recommendation}")
    console.print(f"  Rationale:              [dim]{reason}[/dim]")
    console.print()

    # Summary Panel
    summary_title = Text("SUMMARY & KEY TAKEAWAYS", style="bold bright_cyan")
    console.print(Align.center(summary_title))
    console.print()

    if score >= 8:
        summary_text = (f"[bold bright_green]ATTRACTIVE INVESTMENT OPPORTUNITY[/bold bright_green]\n\n"
                       f"Tesla is trading at ${current_price:.2f}, below our DCF valuation of ${intrinsic_value:.2f}.\n\n"
                       f"Key Strengths:\n"
                       f"[bright_green]•[/bright_green] Significant upside to intrinsic value ({abs(price_diff_pct):.1f}%)\n"
                       f"[bright_green]•[/bright_green] Strong free cash flow generation\n"
                       f"[bright_green]•[/bright_green] Good margin of safety for investors\n"
                       f"[bright_green]•[/bright_green] Reasonable growth assumptions")
    elif score >= 6:
        summary_text = (f"[bold cyan]FAIRLY VALUED WITH MODEST UPSIDE[/bold cyan]\n\n"
                       f"Tesla is trading close to our DCF valuation of ${intrinsic_value:.2f}.\n\n"
                       f"Key Considerations:\n"
                       f"[cyan]•[/cyan] Limited margin of safety\n"
                       f"[cyan]•[/cyan] Growth assumptions are critical to valuation\n"
                       f"[cyan]•[/cyan] Suitable for long-term investors\n"
                       f"[cyan]•[/cyan] Monitor quarterly results closely")
    else:
        summary_text = (f"[bold bright_red]OVERVALUED WITH DOWNSIDE RISK[/bold bright_red]\n\n"
                       f"Tesla is trading at ${current_price:.2f}, above our DCF valuation of ${intrinsic_value:.2f}.\n\n"
                       f"Key Concerns:\n"
                       f"[bright_red]•[/bright_red] Limited upside potential\n"
                       f"[bright_red]•[/bright_red] Downside risk if growth disappoints\n"
                       f"[bright_red]•[/bright_red] Valuation leaves little margin of safety\n"
                       f"[bright_red]•[/bright_red] Consider waiting for better entry point")

    summary_panel = Panel(summary_text, border_style="cyan", style="on black")
    console.print(summary_panel)
    console.print()

    # Sensitivity Analysis Disclaimer
    disclaimer_text = ("[dim]Note: This DCF analysis is based on specific growth and discount rate "
                      "assumptions. Small changes in these assumptions can significantly impact the "
                      "intrinsic value. Always perform sensitivity analysis and consider multiple "
                      "valuation methods before making investment decisions.[/dim]")
    console.print(disclaimer_text)

def main():
    """Main execution function."""
    try:
        # Get financials
        financials = get_tesla_financials()

        # Calculate DCF valuation
        dcf_results = calculate_dcf_valuation(financials)

        # Display analysis
        display_dcf_analysis(financials, dcf_results)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich[/cyan]")

if __name__ == "__main__":
    main()
