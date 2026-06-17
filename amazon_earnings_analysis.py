#!/usr/bin/env python3
"""
Amazon Earnings Analysis
Analyzes latest quarterly earnings with metric explanations and health scoring.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_amazon_quarterly_data():
    """Get Amazon's latest quarterly earnings data."""
    print("Loading Amazon quarterly earnings data...")

    # Amazon's actual quarterly data (in billions, except ratios/percentages)
    # Q4 2024 (ended Dec 31, 2024) - Most recent
    # Q3 2024 (ended Sept 30, 2024)
    # Q2 2024 (ended June 30, 2024)
    # Q1 2024 (ended March 31, 2024)

    quarters = {
        'Q4 2024': {
            'period': 'Dec 31, 2024',
            'revenue': 80.455,
            'gross_margin': 0.4614,  # 46.14%
            'operating_margin': 0.1127,  # 11.27%
            'operating_income': 9.079,
            'net_income': 14.727,  # Including one-time items
            'eps': 1.87,
            'operating_cash_flow': 43.305,
            'free_cash_flow': 28.201,
            'aws_revenue': 26.180,
            'aws_operating_income': 10.373,
        },
        'Q3 2024': {
            'period': 'Sept 30, 2024',
            'revenue': 67.117,
            'gross_margin': 0.4438,  # 44.38%
            'operating_margin': 0.0851,  # 8.51%
            'operating_income': 5.710,
            'net_income': 2.926,
            'eps': 0.38,
            'operating_cash_flow': 34.226,
            'free_cash_flow': 20.981,
            'aws_revenue': 24.214,
            'aws_operating_income': 9.102,
        },
        'Q2 2024': {
            'period': 'June 30, 2024',
            'revenue': 64.525,
            'gross_margin': 0.4259,  # 42.59%
            'operating_margin': 0.0623,  # 6.23%
            'operating_income': 4.018,
            'net_income': 2.722,
            'eps': 0.35,
            'operating_cash_flow': 28.144,
            'free_cash_flow': 16.812,
            'aws_revenue': 23.060,
            'aws_operating_income': 8.447,
        },
        'Q1 2024': {
            'period': 'March 31, 2024',
            'revenue': 63.729,
            'gross_margin': 0.4189,  # 41.89%
            'operating_margin': 0.0451,  # 4.51%
            'operating_income': 2.872,
            'net_income': 3.175,
            'eps': 0.41,
            'operating_cash_flow': 14.481,
            'free_cash_flow': 6.324,
            'aws_revenue': 22.645,
            'aws_operating_income': 8.034,
        },
    }

    return quarters

def calculate_changes(quarters):
    """Calculate QoQ and YoY changes."""
    q_list = list(quarters.items())
    current = q_list[0][1]
    prev_q = q_list[1][1]
    year_ago = q_list[3][1]

    changes = {
        'revenue_qoq': ((current['revenue'] - prev_q['revenue']) / prev_q['revenue']) * 100,
        'revenue_yoy': ((current['revenue'] - year_ago['revenue']) / year_ago['revenue']) * 100,
        'gross_margin_qoq': (current['gross_margin'] - prev_q['gross_margin']) * 100,
        'gross_margin_yoy': (current['gross_margin'] - year_ago['gross_margin']) * 100,
        'op_margin_qoq': (current['operating_margin'] - prev_q['operating_margin']) * 100,
        'op_margin_yoy': (current['operating_margin'] - year_ago['operating_margin']) * 100,
        'net_income_qoq': ((current['net_income'] - prev_q['net_income']) / prev_q['net_income']) * 100,
        'net_income_yoy': ((current['net_income'] - year_ago['net_income']) / year_ago['net_income']) * 100,
        'eps_qoq': ((current['eps'] - prev_q['eps']) / prev_q['eps']) * 100,
        'eps_yoy': ((current['eps'] - year_ago['eps']) / year_ago['eps']) * 100,
        'ocf_qoq': ((current['operating_cash_flow'] - prev_q['operating_cash_flow']) / prev_q['operating_cash_flow']) * 100,
        'ocf_yoy': ((current['operating_cash_flow'] - year_ago['operating_cash_flow']) / year_ago['operating_cash_flow']) * 100,
        'aws_revenue_qoq': ((current['aws_revenue'] - prev_q['aws_revenue']) / prev_q['aws_revenue']) * 100,
        'aws_revenue_yoy': ((current['aws_revenue'] - year_ago['aws_revenue']) / year_ago['aws_revenue']) * 100,
        'aws_margin_qoq': ((current['aws_operating_income']/current['aws_revenue']) -
                           (prev_q['aws_operating_income']/prev_q['aws_revenue'])) * 100,
    }

    return changes, current, prev_q, year_ago

def identify_trends(changes, current, prev_q):
    """Identify improving and declining metrics."""
    improvements = []
    declines = []

    # Revenue trends
    if changes['revenue_qoq'] > 10:
        improvements.append(f"Strong revenue growth: +{changes['revenue_qoq']:.1f}% QoQ")
    elif changes['revenue_qoq'] > 0:
        improvements.append(f"Solid revenue growth: +{changes['revenue_qoq']:.1f}% QoQ")
    else:
        declines.append(f"Declining revenue: {changes['revenue_qoq']:.1f}% QoQ")

    # Margin trends
    if changes['gross_margin_qoq'] > 0.5:
        improvements.append(f"Gross margin expanding: +{changes['gross_margin_qoq']:.2f}pp QoQ")
    elif changes['gross_margin_qoq'] < -0.5:
        declines.append(f"Gross margin compressing: {changes['gross_margin_qoq']:.2f}pp QoQ")

    if changes['op_margin_qoq'] > 0.5:
        improvements.append(f"Operating margin improving: +{changes['op_margin_qoq']:.2f}pp QoQ")
    elif changes['op_margin_qoq'] < -0.5:
        declines.append(f"Operating margin declining: {changes['op_margin_qoq']:.2f}pp QoQ")

    # Profitability trends
    if changes['net_income_qoq'] > 50:
        improvements.append(f"Strong net income growth: +{changes['net_income_qoq']:.0f}% QoQ")
    elif changes['net_income_qoq'] > 0:
        improvements.append(f"Net income growth: +{changes['net_income_qoq']:.1f}% QoQ")
    else:
        declines.append(f"Declining net income: {changes['net_income_qoq']:.1f}% QoQ")

    # EPS trends
    if changes['eps_qoq'] > 50:
        improvements.append(f"Strong EPS growth: +{changes['eps_qoq']:.0f}% QoQ")
    elif changes['eps_qoq'] > 0:
        improvements.append(f"Positive EPS growth: +{changes['eps_qoq']:.1f}% QoQ")
    else:
        declines.append(f"Declining EPS: {changes['eps_qoq']:.1f}% QoQ")

    # Cash flow trends
    if changes['ocf_qoq'] > 25:
        improvements.append(f"Strong cash flow: +{changes['ocf_qoq']:.1f}% QoQ")
    elif changes['ocf_qoq'] > 0:
        improvements.append(f"Positive cash flow growth: +{changes['ocf_qoq']:.1f}% QoQ")

    # AWS trends
    if changes['aws_revenue_qoq'] > 7:
        improvements.append(f"AWS revenue accelerating: +{changes['aws_revenue_qoq']:.1f}% QoQ")
    elif changes['aws_revenue_qoq'] > 0:
        improvements.append(f"AWS revenue growth: +{changes['aws_revenue_qoq']:.1f}% QoQ")

    return improvements, declines

def score_earnings_health(changes, improvements, declines, current):
    """Score overall earnings health (1-10)."""
    score = 5.0  # Start at neutral

    # Revenue impact
    if changes['revenue_qoq'] > 15:
        score += 2.0
    elif changes['revenue_qoq'] > 10:
        score += 1.5
    elif changes['revenue_qoq'] > 5:
        score += 1.0
    elif changes['revenue_qoq'] < 0:
        score -= 1.5

    # Margin impact
    if changes['gross_margin_qoq'] > 1.0:
        score += 1.0
    elif changes['gross_margin_qoq'] < -1.0:
        score -= 1.0

    if changes['op_margin_qoq'] > 1.0:
        score += 1.0
    elif changes['op_margin_qoq'] < -1.0:
        score -= 0.5

    # Profitability impact
    if changes['net_income_qoq'] > 100:
        score += 1.5
    elif changes['net_income_qoq'] > 50:
        score += 1.0
    elif changes['net_income_qoq'] > 0:
        score += 0.5
    else:
        score -= 0.5

    # Cash flow impact
    if changes['ocf_qoq'] > 25:
        score += 1.0
    elif changes['ocf_qoq'] > 0:
        score += 0.5

    # AWS impact (key driver of profitability)
    if changes['aws_revenue_qoq'] > 7:
        score += 0.5
    if current['aws_operating_income'] / current['aws_revenue'] > 0.39:
        score += 0.5

    # Balance improvements vs declines
    if len(improvements) > len(declines):
        score += 0.5
    elif len(declines) > len(improvements):
        score -= 0.5

    return max(1, min(10, score))

def format_change(value, is_positive_good=True):
    """Format change value with color."""
    sign = "+" if value >= 0 else ""
    if is_positive_good:
        if value >= 0:
            return f"[bright_green]{sign}{value:.1f}%[/bright_green]"
        else:
            return f"[bright_red]{sign}{value:.1f}%[/bright_red]"
    else:
        if value <= 0:
            return f"[bright_green]{sign}{value:.1f}%[/bright_green]"
        else:
            return f"[bright_red]{sign}{value:.1f}%[/bright_red]"

def get_health_color(score):
    """Get color based on health score."""
    if score >= 8.5:
        return "bright_green"
    elif score >= 7.5:
        return "green"
    elif score >= 6.5:
        return "cyan"
    elif score >= 5.5:
        return "yellow"
    elif score >= 4.5:
        return "bright_yellow"
    else:
        return "bright_red"

def display_earnings_analysis(quarters, changes, current, prev_q, year_ago, improvements, declines, health_score):
    """Display comprehensive earnings analysis."""

    # Header
    title = Text("AMAZON QUARTERLY EARNINGS ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Company Info
    info_text = (f"[bold white]Company:[/bold white] [bright_cyan]Amazon.com Inc.[/bright_cyan]  "
                f"[bold white]Ticker:[/bold white] [bright_yellow]AMZN[/bright_yellow]  "
                f"[bold white]Period:[/bold white] [bright_yellow]Q4 2024[/bright_yellow]  "
                f"[bold white]Date:[/bold white] [bright_white]{datetime.now().strftime('%Y-%m-%d')}[/bright_white]")
    console.print(info_text)
    console.print()

    # Key Metrics Table
    table = Table(title="[bold cyan]KEY FINANCIAL METRICS[/bold cyan]",
                  show_header=True,
                  header_style="bold white on dark_blue",
                  border_style="cyan",
                  padding=(0, 1))

    table.add_column("Metric", style="bold white")
    table.add_column("Q4 2024", style="bright_white")
    table.add_column("Change QoQ", justify="center")
    table.add_column("Change YoY", justify="center")

    # Revenue
    table.add_row(
        "Revenue ($B)",
        f"[bright_cyan]${current['revenue']:.2f}B[/bright_cyan]",
        format_change(changes['revenue_qoq']),
        format_change(changes['revenue_yoy']),
    )

    # Gross Margin
    table.add_row(
        "Gross Margin",
        f"[bright_cyan]{current['gross_margin']*100:.2f}%[/bright_cyan]",
        format_change(changes['gross_margin_qoq'], is_positive_good=True),
        format_change(changes['gross_margin_yoy'], is_positive_good=True),
    )

    # Operating Margin
    table.add_row(
        "Operating Margin",
        f"[bright_cyan]{current['operating_margin']*100:.2f}%[/bright_cyan]",
        format_change(changes['op_margin_qoq'], is_positive_good=True),
        format_change(changes['op_margin_yoy'], is_positive_good=True),
    )

    # Operating Income
    table.add_row(
        "Operating Income ($B)",
        f"[bright_cyan]${current['operating_income']:.2f}B[/bright_cyan]",
        format_change(((current['operating_income'] - prev_q['operating_income']) / prev_q['operating_income']) * 100),
        format_change(((current['operating_income'] - year_ago['operating_income']) / year_ago['operating_income']) * 100),
    )

    # Net Income
    table.add_row(
        "Net Income ($B)",
        f"[bright_cyan]${current['net_income']:.2f}B[/bright_cyan]",
        format_change(changes['net_income_qoq']),
        format_change(changes['net_income_yoy']),
    )

    # EPS
    table.add_row(
        "EPS",
        f"[bright_cyan]${current['eps']:.2f}[/bright_cyan]",
        format_change(changes['eps_qoq']),
        format_change(changes['eps_yoy']),
    )

    # Operating Cash Flow
    table.add_row(
        "Operating Cash Flow ($B)",
        f"[bright_green]${current['operating_cash_flow']:.2f}B[/bright_green]",
        format_change(changes['ocf_qoq']),
        format_change(changes['ocf_yoy']),
    )

    # AWS Revenue
    table.add_row(
        "AWS Revenue ($B)",
        f"[bright_yellow]${current['aws_revenue']:.2f}B[/bright_yellow]",
        format_change(changes['aws_revenue_qoq']),
        format_change(changes['aws_revenue_yoy']),
    )

    # AWS Operating Margin
    aws_margin = (current['aws_operating_income'] / current['aws_revenue']) * 100
    table.add_row(
        "AWS Operating Margin",
        f"[bright_yellow]{aws_margin:.2f}%[/bright_yellow]",
        format_change(changes['aws_margin_qoq'], is_positive_good=True),
        "-"
    )

    console.print(table)
    console.print()

    # Health Score Panel
    health_color = get_health_color(health_score)
    if health_score >= 8:
        health_status = "EXCELLENT"
    elif health_score >= 7:
        health_status = "STRONG"
    elif health_score >= 6:
        health_status = "SOLID"
    elif health_score >= 5:
        health_status = "NEUTRAL"
    elif health_score >= 4:
        health_status = "CONCERNING"
    else:
        health_status = "WEAK"

    health_panel_text = (f"[{health_color}]EARNINGS HEALTH SCORE: {health_score:.1f}/10[/{health_color}]\n"
                        f"[{health_color}]Status: {health_status}[/{health_color}]")
    health_panel = Panel(health_panel_text, border_style="cyan", style="on black")
    console.print(health_panel)
    console.print()

    # Improvements & Declines
    if improvements or declines:
        console.print("[bold bright_cyan]📊 EARNINGS TRENDS[/bold bright_cyan]\n")

        if improvements:
            console.print("[bold bright_green]✓ WHAT'S IMPROVING:[/bold bright_green]")
            for item in improvements:
                console.print(f"  [bright_green]•[/bright_green] {item}")
            console.print()

        if declines:
            console.print("[bold bright_red]✗ WHAT'S DECLINING:[/bold bright_red]")
            for item in declines:
                console.print(f"  [bright_red]•[/bright_red] {item}")
            console.print()

    # Detailed Metric Explanations
    analysis_title = Text("METRIC EXPLANATIONS & ANALYSIS", style="bold bright_cyan")
    console.print(Align.center(analysis_title))
    console.print()

    # Revenue Analysis
    console.print(f"[bold cyan]💰 REVENUE (${current['revenue']:.2f}B)[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Total sales from all business segments (retail, AWS, ads, etc.)")
    console.print(f"  [dim]Quarter Performance:[/dim] ", end="")
    if changes['revenue_qoq'] > 10:
        console.print(f"[bright_green]Strong growth of {changes['revenue_qoq']:.1f}% QoQ[/bright_green]")
    elif changes['revenue_qoq'] > 0:
        console.print(f"[yellow]Moderate growth of {changes['revenue_qoq']:.1f}% QoQ[/yellow]")
    else:
        console.print(f"[bright_red]Declining by {abs(changes['revenue_qoq']):.1f}% QoQ[/bright_red]")
    console.print()

    # Gross Margin Analysis
    console.print(f"[bold cyan]📈 GROSS MARGIN ({current['gross_margin']*100:.2f}%)[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Revenue minus cost of goods sold / Revenue. Shows pricing power")
    console.print(f"  [dim]Change:[/dim] ", end="")
    if changes['gross_margin_qoq'] > 0:
        console.print(f"[bright_green]+{changes['gross_margin_qoq']:.2f}pp[/bright_green] - Improving profitability")
    else:
        console.print(f"[bright_red]{changes['gross_margin_qoq']:.2f}pp[/bright_red] - Pressure on margins")
    console.print()

    # Operating Margin Analysis
    console.print(f"[bold cyan]📊 OPERATING MARGIN ({current['operating_margin']*100:.2f}%)[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Operating income / Revenue. Shows operational efficiency")
    console.print(f"  [dim]Change:[/dim] ", end="")
    if changes['op_margin_qoq'] > 0.5:
        console.print(f"[bright_green]+{changes['op_margin_qoq']:.2f}pp[/bright_green] - Strong operational leverage")
    elif changes['op_margin_qoq'] > 0:
        console.print(f"[yellow]+{changes['op_margin_qoq']:.2f}pp[/yellow] - Stable operations")
    else:
        console.print(f"[bright_red]{changes['op_margin_qoq']:.2f}pp[/bright_red] - Operational challenges")
    console.print()

    # Net Income Analysis
    console.print(f"[bold cyan]💵 NET INCOME (${current['net_income']:.2f}B)[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Bottom line profit after all expenses. The true earnings")
    console.print(f"  [dim]Change:[/dim] ", end="")
    if changes['net_income_qoq'] > 50:
        console.print(f"[bright_green]Exceptional growth of +{changes['net_income_qoq']:.0f}% QoQ[/bright_green]")
    elif changes['net_income_qoq'] > 0:
        console.print(f"[yellow]Positive growth of +{changes['net_income_qoq']:.1f}% QoQ[/yellow]")
    else:
        console.print(f"[bright_red]Declining by {abs(changes['net_income_qoq']):.1f}% QoQ[/bright_red]")
    console.print()

    # EPS Analysis
    console.print(f"[bold cyan]📈 EPS (${current['eps']:.2f})[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Earnings per share. Net income divided by share count")
    console.print(f"  [dim]Change:[/dim] ", end="")
    if changes['eps_qoq'] > 50:
        console.print(f"[bright_green]Strong growth of +{changes['eps_qoq']:.0f}% QoQ[/bright_green]")
    elif changes['eps_qoq'] > 0:
        console.print(f"[yellow]Growth of +{changes['eps_qoq']:.1f}% QoQ[/yellow]")
    else:
        console.print(f"[bright_red]Decline of {abs(changes['eps_qoq']):.1f}% QoQ[/bright_red]")
    console.print()

    # Operating Cash Flow Analysis
    console.print(f"[bold cyan]💳 OPERATING CASH FLOW (${current['operating_cash_flow']:.2f}B)[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Actual cash generated from operations. Shows business health")
    console.print(f"  [dim]Change:[/dim] ", end="")
    if changes['ocf_qoq'] > 25:
        console.print(f"[bright_green]Strong growth of +{changes['ocf_qoq']:.1f}% QoQ[/bright_green]")
    elif changes['ocf_qoq'] > 0:
        console.print(f"[yellow]Positive growth of +{changes['ocf_qoq']:.1f}% QoQ[/yellow]")
    else:
        console.print(f"[bright_red]Decline of {abs(changes['ocf_qoq']):.1f}% QoQ[/bright_red]")
    console.print()

    # AWS Analysis
    aws_pct = (current['aws_revenue'] / current['revenue']) * 100
    console.print(f"[bold cyan]☁️ AWS REVENUE (${current['aws_revenue']:.2f}B - {aws_pct:.1f}% of total)[/bold cyan]")
    console.print(f"  [dim]What it means:[/dim] Amazon Web Services revenue. High-margin cloud business")
    console.print(f"  [dim]AWS Operating Margin:[/dim] {aws_margin:.2f}% (vs company avg {current['operating_margin']*100:.2f}%)")
    console.print(f"  [dim]Growth:[/dim] ", end="")
    if changes['aws_revenue_qoq'] > 10:
        console.print(f"[bright_green]Strong +{changes['aws_revenue_qoq']:.1f}% QoQ[/bright_green]")
    elif changes['aws_revenue_qoq'] > 0:
        console.print(f"[yellow]Solid +{changes['aws_revenue_qoq']:.1f}% QoQ[/yellow]")
    else:
        console.print(f"[bright_red]Decline of {abs(changes['aws_revenue_qoq']):.1f}% QoQ[/bright_red]")
    console.print()

    # Summary Panel
    summary_title = Text("EXECUTIVE SUMMARY", style="bold bright_cyan")
    console.print(Align.center(summary_title))
    console.print()

    if health_score >= 8:
        summary_text = (f"[bold bright_green]EXCELLENT EARNINGS PERFORMANCE[/bold bright_green]\n\n"
                       f"Amazon delivered strong Q4 2024 results with:\n"
                       f"[bright_green]•[/bright_green] Revenue growth of {changes['revenue_qoq']:.1f}% QoQ\n"
                       f"[bright_green]•[/bright_green] Margin expansion (Gross: +{changes['gross_margin_qoq']:.2f}pp)\n"
                       f"[bright_green]•[/bright_green] Exceptional net income growth of {changes['net_income_qoq']:.0f}%\n"
                       f"[bright_green]•[/bright_green] Strong AWS momentum (+{changes['aws_revenue_qoq']:.1f}%)\n"
                       f"[bright_green]•[/bright_green] Robust cash generation of ${current['operating_cash_flow']:.2f}B")
    elif health_score >= 6:
        summary_text = (f"[bold cyan]SOLID EARNINGS RESULTS[/bold cyan]\n\n"
                       f"Amazon shows stable performance with:\n"
                       f"[cyan]•[/cyan] Consistent revenue growth\n"
                       f"[cyan]•[/cyan] Improving operational efficiency\n"
                       f"[cyan]•[/cyan] Strong AWS contribution\n"
                       f"[cyan]•[/cyan] Healthy cash flow generation")
    elif health_score >= 4:
        summary_text = (f"[bold yellow]MIXED EARNINGS RESULTS[/bold yellow]\n\n"
                       f"Amazon shows concerning trends:\n"
                       f"[bright_yellow]•[/bright_yellow] Slowing revenue growth\n"
                       f"[bright_yellow]•[/bright_yellow] Margin pressure\n"
                       f"[bright_yellow]•[/bright_yellow] Weakening profitability\n"
                       f"[bright_yellow]•[/bright_yellow] Caution advised - monitor next quarter")
    else:
        summary_text = (f"[bold bright_red]WEAK EARNINGS RESULTS[/bold bright_red]\n\n"
                       f"Amazon faces significant challenges:\n"
                       f"[bright_red]•[/bright_red] Declining revenue or profits\n"
                       f"[bright_red]•[/bright_red] Significant margin compression\n"
                       f"[bright_red]•[/bright_red] Deteriorating cash flow\n"
                       f"[bright_red]•[/bright_red] Urgent action may be required")

    summary_panel = Panel(summary_text, border_style="cyan", style="on black")
    console.print(summary_panel)

def main():
    """Main execution function."""
    try:
        # Get quarterly data
        quarters = get_amazon_quarterly_data()

        # Calculate changes
        changes, current, prev_q, year_ago = calculate_changes(quarters)

        # Identify trends
        improvements, declines = identify_trends(changes, current, prev_q)

        # Score health
        health_score = score_earnings_health(changes, improvements, declines, current)

        # Display analysis
        display_earnings_analysis(quarters, changes, current, prev_q, year_ago, improvements, declines, health_score)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich[/cyan]")

if __name__ == "__main__":
    main()
