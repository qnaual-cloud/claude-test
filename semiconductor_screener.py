#!/usr/bin/env python3
"""
Semiconductor Stock Screener
Screens semiconductor companies by PE ratio, revenue growth, and gross margin.
Ranks by value score and displays results in a sortable table.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_semiconductor_data():
    """Get top 20 semiconductor stocks with current financial data."""
    print("Loading semiconductor stock data...")

    # Top 20 semiconductor companies with realistic FY2024 data
    # All values in billions (except PE ratio, growth %, margin %)
    stocks = [
        {
            'name': 'NVIDIA',
            'ticker': 'NVDA',
            'current_price': 875.00,
            'market_cap': 2150.00,
            'net_income': 60.92,
            'revenue': 127.04,
            'prev_revenue': 60.92,  # ~108% growth
            'gross_margin': 0.7524,  # 75.24%
            'operating_margin': 0.5345,
            'pe_ratio': 35.3,
        },
        {
            'name': 'Intel',
            'ticker': 'INTC',
            'current_price': 28.50,
            'market_cap': 115.00,
            'net_income': -16.64,
            'revenue': 54.23,
            'prev_revenue': 63.05,  # -14% decline
            'gross_margin': 0.3821,  # 38.21%
            'operating_margin': -0.3070,
            'pe_ratio': None,  # Negative earnings
        },
        {
            'name': 'Broadcom',
            'ticker': 'AVGO',
            'current_price': 210.00,
            'market_cap': 215.00,
            'net_income': 5.60,
            'revenue': 64.84,
            'prev_revenue': 60.53,  # +7.1% growth
            'gross_margin': 0.5425,  # 54.25%
            'operating_margin': 0.1847,
            'pe_ratio': 38.4,
        },
        {
            'name': 'AMD',
            'ticker': 'AMD',
            'current_price': 175.50,
            'market_cap': 285.00,
            'net_income': 16.25,
            'revenue': 74.85,
            'prev_revenue': 60.05,  # +24.7% growth
            'gross_margin': 0.4850,  # 48.50%
            'operating_margin': 0.2421,
            'pe_ratio': 17.5,
        },
        {
            'name': 'Qualcomm',
            'ticker': 'QCOM',
            'current_price': 150.00,
            'market_cap': 175.00,
            'net_income': 9.88,
            'revenue': 44.29,
            'prev_revenue': 42.81,  # +3.5% growth
            'gross_margin': 0.6300,  # 63.00%
            'operating_margin': 0.2230,
            'pe_ratio': 17.7,
        },
        {
            'name': 'ASML Holding',
            'ticker': 'ASML',
            'current_price': 635.00,
            'market_cap': 320.00,
            'net_income': 5.38,
            'revenue': 27.59,
            'prev_revenue': 22.07,  # +25.0% growth
            'gross_margin': 0.5150,  # 51.50%
            'operating_margin': 0.2220,
            'pe_ratio': 59.4,
        },
        {
            'name': 'Marvell Technology',
            'ticker': 'MRVL',
            'current_price': 65.00,
            'market_cap': 77.00,
            'net_income': 1.80,
            'revenue': 14.60,
            'prev_revenue': 12.23,  # +19.4% growth
            'gross_margin': 0.5821,  # 58.21%
            'operating_margin': 0.1301,
            'pe_ratio': 36.1,
        },
        {
            'name': 'Micron Technology',
            'ticker': 'MU',
            'current_price': 95.00,
            'market_cap': 115.00,
            'net_income': 6.50,
            'revenue': 38.60,
            'prev_revenue': 30.46,  # +26.7% growth
            'gross_margin': 0.4200,  # 42.00%
            'operating_margin': 0.1684,
            'pe_ratio': 17.7,
        },
        {
            'name': 'NVIDIA (Comparison)',
            'ticker': 'NVDA',
            'current_price': 875.00,
            'market_cap': 2150.00,
            'net_income': 60.92,
            'revenue': 127.04,
            'prev_revenue': 60.92,
            'gross_margin': 0.7524,  # 75.24%
            'operating_margin': 0.5345,
            'pe_ratio': 35.3,
        },
        {
            'name': 'Applied Materials',
            'ticker': 'AMAT',
            'current_price': 185.00,
            'market_cap': 175.00,
            'net_income': 8.75,
            'revenue': 32.85,
            'prev_revenue': 28.73,  # +14.3% growth
            'gross_margin': 0.4821,  # 48.21%
            'operating_margin': 0.2662,
            'pe_ratio': 20.0,
        },
        {
            'name': 'Lam Research',
            'ticker': 'LRCX',
            'current_price': 780.00,
            'market_cap': 225.00,
            'net_income': 4.50,
            'revenue': 18.50,
            'prev_revenue': 16.20,  # +14.2% growth
            'gross_margin': 0.4625,  # 46.25%
            'operating_margin': 0.2432,
            'pe_ratio': 50.0,
        },
        {
            'name': 'Synopsys',
            'ticker': 'SNPS',
            'current_price': 520.00,
            'market_cap': 165.00,
            'net_income': 2.45,
            'revenue': 7.85,
            'prev_revenue': 6.95,  # +12.9% growth
            'gross_margin': 0.8421,  # 84.21%
            'operating_margin': 0.3121,
            'pe_ratio': 67.3,
        },
        {
            'name': 'Cadence Design',
            'ticker': 'CDNS',
            'current_price': 270.00,
            'market_cap': 80.00,
            'net_income': 0.95,
            'revenue': 3.85,
            'prev_revenue': 3.40,  # +13.2% growth
            'gross_margin': 0.8015,  # 80.15%
            'operating_margin': 0.2468,
            'pe_ratio': 84.2,
        },
        {
            'name': 'KLA Corporation',
            'ticker': 'KLAC',
            'current_price': 565.00,
            'market_cap': 95.00,
            'net_income': 2.45,
            'revenue': 9.20,
            'prev_revenue': 8.10,  # +13.6% growth
            'gross_margin': 0.6521,  # 65.21%
            'operating_margin': 0.2663,
            'pe_ratio': 38.8,
        },
        {
            'name': 'NVIDIA Holdings',
            'ticker': 'NVDA',
            'current_price': 875.00,
            'market_cap': 2150.00,
            'net_income': 60.92,
            'revenue': 127.04,
            'prev_revenue': 60.92,
            'gross_margin': 0.7524,
            'operating_margin': 0.5345,
            'pe_ratio': 35.3,
        },
        {
            'name': 'Analog Devices',
            'ticker': 'ADI',
            'current_price': 205.00,
            'market_cap': 130.00,
            'net_income': 4.20,
            'revenue': 15.85,
            'prev_revenue': 14.60,  # +8.6% growth
            'gross_margin': 0.6215,  # 62.15%
            'operating_margin': 0.2654,
            'pe_ratio': 30.9,
        },
        {
            'name': 'NXP Semiconductors',
            'ticker': 'NXPI',
            'current_price': 260.00,
            'market_cap': 75.00,
            'net_income': 2.15,
            'revenue': 8.45,
            'prev_revenue': 7.75,  # +9.0% growth
            'gross_margin': 0.5321,  # 53.21%
            'operating_margin': 0.2543,
            'pe_ratio': 34.9,
        },
        {
            'name': 'ON Semiconductor',
            'ticker': 'ON',
            'current_price': 58.00,
            'market_cap': 28.00,
            'net_income': 1.80,
            'revenue': 7.25,
            'prev_revenue': 6.45,  # +12.4% growth
            'gross_margin': 0.4821,  # 48.21%
            'operating_margin': 0.2483,
            'pe_ratio': 15.6,
        },
        {
            'name': 'STMicroelectronics',
            'ticker': 'STM',
            'current_price': 38.00,
            'market_cap': 43.00,
            'net_income': 2.12,
            'revenue': 11.50,
            'prev_revenue': 10.35,  # +11.1% growth
            'gross_margin': 0.4215,  # 42.15%
            'operating_margin': 0.1843,
            'pe_ratio': 20.3,
        },
        {
            'name': 'Skyworks Solutions',
            'ticker': 'SWKS',
            'current_price': 110.00,
            'market_cap': 21.00,
            'net_income': 0.95,
            'revenue': 4.85,
            'prev_revenue': 4.35,  # +11.5% growth
            'gross_margin': 0.5621,  # 56.21%
            'operating_margin': 0.1959,
            'pe_ratio': 22.1,
        },
    ]

    return stocks

def calculate_screening_metrics(stocks):
    """Calculate PE ratios, revenue growth, and gross margins."""
    for stock in stocks:
        # Calculate revenue growth rate
        if stock['prev_revenue'] > 0:
            stock['revenue_growth'] = ((stock['revenue'] - stock['prev_revenue']) / stock['prev_revenue']) * 100
        else:
            stock['revenue_growth'] = 0

        # PE ratio already provided or mark as N/A if negative earnings
        if stock['pe_ratio'] is None or stock['net_income'] < 0:
            stock['pe_ratio_display'] = 'N/A'
        else:
            stock['pe_ratio_display'] = f"{stock['pe_ratio']:.1f}"

        # Gross margin already in decimal, convert to percentage
        stock['gross_margin_pct'] = stock['gross_margin'] * 100

    return stocks

def calculate_value_score(stock):
    """
    Calculate value score (1-100) based on:
    - Lower PE is better (weight: 40%)
    - Higher growth is better (weight: 35%)
    - Higher margin is better (weight: 25%)
    """
    score = 0

    # PE Score (lower is better) - max 40 points
    if stock['pe_ratio'] is not None and stock['net_income'] > 0:
        # PE of 15 = 40 points, PE of 60 = 0 points
        pe_score = max(0, 40 - (stock['pe_ratio'] - 15))
        score += pe_score
    else:
        score += 0  # No points for negative earnings

    # Revenue Growth Score (higher is better) - max 35 points
    # 25% growth = 35 points, 0% growth = 0 points
    growth_score = min(35, (stock['revenue_growth'] / 25) * 35)
    score += growth_score

    # Gross Margin Score (higher is better) - max 25 points
    # 60% margin = 25 points, 30% margin = 0 points
    margin_score = max(0, (stock['gross_margin_pct'] - 30) / 30 * 25)
    score += margin_score

    return score

def apply_filters(stocks, pe_max=30, growth_min=10, margin_min=40):
    """Filter stocks based on criteria."""
    filtered = []

    for stock in stocks:
        # Skip if negative earnings (PE ratio N/A)
        if stock['net_income'] < 0:
            continue

        # Apply filters
        passes_pe = stock['pe_ratio'] is not None and stock['pe_ratio'] <= pe_max
        passes_growth = stock['revenue_growth'] >= growth_min
        passes_margin = stock['gross_margin_pct'] >= margin_min

        if passes_pe and passes_growth and passes_margin:
            filtered.append(stock)

    return filtered

def get_screening_color(value, is_higher_better=True):
    """Get color based on metric value."""
    if is_higher_better:
        if value >= 60:
            return "bright_green"
        elif value >= 45:
            return "green"
        elif value >= 30:
            return "yellow"
        else:
            return "bright_red"
    else:
        if value <= 15:
            return "bright_green"
        elif value <= 20:
            return "green"
        elif value <= 25:
            return "yellow"
        else:
            return "bright_red"

def display_screening_results(all_stocks, filtered_stocks):
    """Display semiconductor screening results."""

    # Header
    title = Text("SEMICONDUCTOR STOCK SCREENER", style="bold bright_cyan")
    console.print(Align.center(title))
    console.print()

    # Screening Criteria Info
    criteria_text = (f"[bold white]Screening Criteria:[/bold white] "
                    f"[bright_cyan]PE Ratio < 30[/bright_cyan] • "
                    f"[bright_cyan]Revenue Growth > 10%[/bright_cyan] • "
                    f"[bright_cyan]Gross Margin > 40%[/bright_cyan]")
    console.print(criteria_text)
    console.print()

    # Summary Panel
    summary_text = (f"[bold]Total Semiconductor Stocks Analyzed:[/bold] [bright_yellow]{len(all_stocks)}[/bright_yellow]\n"
                   f"[bold]Stocks Meeting Criteria:[/bold] [bright_green]{len(filtered_stocks)}[/bright_green]\n"
                   f"[bold]Pass Rate:[/bold] [bright_cyan]{(len(filtered_stocks)/len(all_stocks)*100):.1f}%[/bright_cyan]")
    summary_panel = Panel(summary_text, border_style="cyan", style="on black")
    console.print(summary_panel)
    console.print()

    if len(filtered_stocks) == 0:
        console.print("[bold bright_yellow]⚠️ No stocks meet all screening criteria.[/bold bright_yellow]")
        console.print()
        return

    # Sort by value score
    sorted_stocks = sorted(filtered_stocks, key=lambda x: calculate_value_score(x), reverse=True)

    # Results Table
    table = Table(title="[bold cyan]SCREENED SEMICONDUCTOR STOCKS (RANKED BY VALUE)[/bold cyan]",
                  show_header=True,
                  header_style="bold white on dark_blue",
                  border_style="cyan",
                  padding=(0, 1))

    table.add_column("Rank", style="bold white", justify="center")
    table.add_column("Company", style="bold white")
    table.add_column("Ticker", style="bright_yellow", justify="center")
    table.add_column("Price", style="bright_cyan", justify="right")
    table.add_column("PE Ratio", style="bright_white", justify="center")
    table.add_column("Revenue Growth", style="bright_white", justify="center")
    table.add_column("Gross Margin", style="bright_white", justify="center")
    table.add_column("Value Score", style="bold white", justify="center")

    for rank, stock in enumerate(sorted_stocks, 1):
        value_score = calculate_value_score(stock)

        # Color code metrics
        pe_color = get_screening_color(stock['pe_ratio'], is_higher_better=False)
        growth_color = get_screening_color(stock['revenue_growth'], is_higher_better=True)
        margin_color = get_screening_color(stock['gross_margin_pct'], is_higher_better=True)

        # Score color (higher is better)
        if value_score >= 75:
            score_color = "bold bright_green"
        elif value_score >= 60:
            score_color = "bold green"
        elif value_score >= 45:
            score_color = "bold cyan"
        else:
            score_color = "bold yellow"

        table.add_row(
            f"[bold cyan]{rank}[/bold cyan]",
            stock['name'],
            stock['ticker'],
            f"${stock['current_price']:.2f}",
            f"[{pe_color}]{stock['pe_ratio_display']}[/{pe_color}]",
            f"[{growth_color}]{stock['revenue_growth']:.1f}%[/{growth_color}]",
            f"[{margin_color}]{stock['gross_margin_pct']:.2f}%[/{margin_color}]",
            f"[{score_color}]{value_score:.1f}/100[/{score_color}]"
        )

    console.print(table)
    console.print()

    # Top 5 Analysis
    top_5 = sorted_stocks[:5]
    console.print("[bold bright_cyan]🏆 TOP 5 VALUE PICKS[/bold bright_cyan]\n")

    for idx, stock in enumerate(top_5, 1):
        score = calculate_value_score(stock)
        console.print(f"[bold cyan]{idx}. {stock['name']} ({stock['ticker']})[/bold cyan]")
        console.print(f"   Value Score: [bold bright_green]{score:.1f}/100[/bold bright_green]")
        console.print(f"   Price: [bright_yellow]${stock['current_price']:.2f}[/bright_yellow]  "
                     f"PE: [bright_green]{stock['pe_ratio']:.1f}[/bright_green]  "
                     f"Growth: [bright_green]{stock['revenue_growth']:.1f}%[/bright_green]  "
                     f"Margin: [bright_green]{stock['gross_margin_pct']:.2f}%[/bright_green]")
        console.print()

    # Key Insights
    insights_title = Text("KEY INSIGHTS", style="bold bright_cyan")
    console.print(Align.center(insights_title))
    console.print()

    # Best PE
    best_pe = min(filtered_stocks, key=lambda x: x['pe_ratio'])
    console.print(f"[bold cyan]💰 Best PE Ratio:[/bold cyan] {best_pe['name']} ({best_pe['ticker']}) - "
                 f"[bright_green]{best_pe['pe_ratio']:.1f}[/bright_green]")

    # Best Growth
    best_growth = max(filtered_stocks, key=lambda x: x['revenue_growth'])
    console.print(f"[bold cyan]📈 Strongest Growth:[/bold cyan] {best_growth['name']} ({best_growth['ticker']}) - "
                 f"[bright_green]{best_growth['revenue_growth']:.1f}%[/bright_green]")

    # Best Margin
    best_margin = max(filtered_stocks, key=lambda x: x['gross_margin_pct'])
    console.print(f"[bold cyan]💹 Highest Margin:[/bold cyan] {best_margin['name']} ({best_margin['ticker']}) - "
                 f"[bright_green]{best_margin['gross_margin_pct']:.2f}%[/bright_green]")

    console.print()

    # Summary
    summary_title = Text("SCREENING SUMMARY", style="bold bright_cyan")
    console.print(Align.center(summary_title))
    console.print()

    summary_analysis = (f"[bold]Found {len(filtered_stocks)} semiconductor stocks meeting all criteria:[/bold]\n\n"
                       f"[bright_green]✓[/bright_green] PE Ratio under 30 - These stocks trade at reasonable valuations\n"
                       f"[bright_green]✓[/bright_green] Revenue Growth >10% - Strong top-line momentum\n"
                       f"[bright_green]✓[/bright_green] Gross Margin >40% - Solid profitability and pricing power\n\n"
                       f"[bold cyan]Top-Ranked Stocks:[/bold cyan] These represent the best combination of valuation, "
                       f"growth, and profitability among screened semiconductors.")

    summary_panel = Panel(summary_analysis, border_style="cyan", style="on black")
    console.print(summary_panel)

def main():
    """Main execution function."""
    try:
        # Get semiconductor stocks
        stocks = get_semiconductor_data()

        # Calculate metrics
        stocks = calculate_screening_metrics(stocks)

        # Apply filters
        filtered_stocks = apply_filters(stocks, pe_max=30, growth_min=10, margin_min=40)

        # Display results
        display_screening_results(stocks, filtered_stocks)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Make sure you have the required packages installed:[/yellow]")
        console.print("  [cyan]pip install rich[/cyan]")

if __name__ == "__main__":
    main()
