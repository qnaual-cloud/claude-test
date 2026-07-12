#!/usr/bin/env python3
"""
Semiconductor Stock Screener
Screen top semiconductor stocks by PE ratio, revenue growth, and gross margin.
Find value picks meeting specific criteria with vibrant demo formatting.
"""

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_semiconductor_stocks():
    """Get 20 semiconductor stocks with financial data."""
    print("Loading semiconductor stock data...\n")

    stocks = [
        {
            'ticker': 'NVDA',
            'company': 'NVIDIA Corporation',
            'price': 875.00,
            'pe_ratio': 62.5,
            'revenue_growth': 126.0,
            'gross_margin': 69.5,
            'market_cap': 2150.0,
            'sector': 'GPU/AI',
        },
        {
            'ticker': 'AMD',
            'company': 'Advanced Micro Devices',
            'price': 156.20,
            'pe_ratio': 18.5,
            'revenue_growth': 16.0,
            'gross_margin': 48.2,
            'market_cap': 255.0,
            'sector': 'Processors',
        },
        {
            'ticker': 'QCOM',
            'company': 'Qualcomm Inc.',
            'price': 198.50,
            'pe_ratio': 22.0,
            'revenue_growth': 14.5,
            'gross_margin': 61.3,
            'market_cap': 225.0,
            'sector': 'Mobile/5G',
        },
        {
            'ticker': 'AVGO',
            'company': 'Broadcom Inc.',
            'price': 189.75,
            'pe_ratio': 24.5,
            'revenue_growth': 12.8,
            'gross_margin': 54.7,
            'market_cap': 95.0,
            'sector': 'Infrastructure',
        },
        {
            'ticker': 'MRVL',
            'company': 'Marvell Technology',
            'price': 92.30,
            'pe_ratio': 26.0,
            'revenue_growth': 18.5,
            'gross_margin': 63.5,
            'market_cap': 79.0,
            'sector': 'Data Center',
        },
        {
            'ticker': 'LRCX',
            'company': 'Lam Research',
            'price': 780.00,
            'pe_ratio': 28.5,
            'revenue_growth': 11.2,
            'gross_margin': 47.8,
            'market_cap': 115.0,
            'sector': 'Equipment',
        },
        {
            'ticker': 'ASML',
            'company': 'ASML Holding',
            'price': 820.50,
            'pe_ratio': 45.0,
            'revenue_growth': 9.5,
            'gross_margin': 52.1,
            'market_cap': 340.0,
            'sector': 'Equipment',
        },
        {
            'ticker': 'SLAB',
            'company': 'Silicon Labs',
            'price': 185.40,
            'pe_ratio': 32.5,
            'revenue_growth': 13.2,
            'gross_margin': 68.9,
            'market_cap': 27.5,
            'sector': 'IoT/Analog',
        },
        {
            'ticker': 'NXPI',
            'company': 'NXP Semiconductors',
            'price': 210.80,
            'pe_ratio': 20.5,
            'revenue_growth': 15.8,
            'gross_margin': 46.2,
            'market_cap': 58.0,
            'sector': 'Automotive/IoT',
        },
        {
            'ticker': 'MPWR',
            'company': 'Monolithic Power Systems',
            'price': 620.25,
            'pe_ratio': 35.8,
            'revenue_growth': 21.5,
            'gross_margin': 59.2,
            'market_cap': 29.5,
            'sector': 'Power Management',
        },
        {
            'ticker': 'ON',
            'company': 'ON Semiconductor',
            'price': 42.15,
            'pe_ratio': 13.2,
            'revenue_growth': 11.8,
            'gross_margin': 43.5,
            'market_cap': 18.5,
            'sector': 'Discrete/Analog',
        },
        {
            'ticker': 'STM',
            'company': 'STMicroelectronics',
            'price': 45.80,
            'pe_ratio': 15.5,
            'revenue_growth': 12.2,
            'gross_margin': 41.8,
            'market_cap': 47.0,
            'sector': 'Mixed Signal',
        },
        {
            'ticker': 'NXPI',
            'company': 'NXP Semiconductors',
            'price': 210.80,
            'pe_ratio': 20.5,
            'revenue_growth': 15.8,
            'gross_margin': 46.2,
            'market_cap': 58.0,
            'sector': 'Automotive/IoT',
        },
        {
            'ticker': 'SEMI',
            'company': 'Semtech Corporation',
            'price': 28.50,
            'pe_ratio': 24.8,
            'revenue_growth': 9.2,
            'gross_margin': 55.3,
            'market_cap': 1.8,
            'sector': 'Analog/Mixed-Signal',
        },
        {
            'ticker': 'TXIM',
            'company': 'Teledyne Technologies',
            'price': 515.50,
            'pe_ratio': 18.8,
            'revenue_growth': 13.5,
            'gross_margin': 45.1,
            'market_cap': 25.0,
            'sector': 'Imaging/Sensors',
        },
        {
            'ticker': 'MXIM',
            'company': 'Maxim Integrated',
            'price': 85.20,
            'pe_ratio': 21.5,
            'revenue_growth': 14.2,
            'gross_margin': 60.8,
            'market_cap': 23.0,
            'sector': 'Analog',
        },
        {
            'ticker': 'SiS',
            'company': 'Silicon Image (Lattice)',
            'price': 72.35,
            'pe_ratio': 27.2,
            'revenue_growth': 16.8,
            'gross_margin': 58.5,
            'market_cap': 5.2,
            'sector': 'Video/Connectivity',
        },
        {
            'ticker': 'IROQ',
            'company': 'Iroquois Technologies',
            'price': 156.80,
            'pe_ratio': 19.5,
            'revenue_growth': 17.3,
            'gross_margin': 62.1,
            'market_cap': 8.5,
            'sector': 'Signal Processing',
        },
        {
            'ticker': 'SGTX',
            'company': 'Sigma Systems',
            'price': 198.45,
            'pe_ratio': 23.8,
            'revenue_growth': 11.5,
            'gross_margin': 49.7,
            'market_cap': 12.0,
            'sector': 'Storage/Networking',
        },
        {
            'ticker': 'CRWD',
            'company': 'Crowdstrike (Sensors)',
            'price': 385.20,
            'pe_ratio': 29.5,
            'revenue_growth': 22.8,
            'gross_margin': 73.2,
            'market_cap': 60.0,
            'sector': 'Security/Sensors',
        },
    ]

    return stocks

def calculate_value_score(stock):
    """Calculate composite value score."""
    pe_score = max(0, (50 - stock['pe_ratio']) / 50) * 40  # 40% weight, inverted (lower PE is better)
    growth_score = min(stock['revenue_growth'] / 25, 1.0) * 35  # 35% weight
    margin_score = (stock['gross_margin'] / 75) * 25  # 25% weight

    total_score = pe_score + growth_score + margin_score
    return round(total_score, 1)

def meets_criteria(stock):
    """Check if stock meets screening criteria."""
    return stock['pe_ratio'] < 30 and stock['revenue_growth'] > 10 and stock['gross_margin'] > 40

def get_score_color(score):
    """Get color based on value score."""
    if score >= 75:
        return 'bold bright_green'
    elif score >= 65:
        return 'bold bright_green'
    elif score >= 55:
        return 'bold bright_yellow'
    else:
        return 'bright_cyan'

def get_metric_color(metric, value):
    """Get color based on metric value."""
    if metric == 'pe_ratio':
        if value < 15:
            return 'bold bright_green'
        elif value < 20:
            return 'bright_green'
        elif value < 25:
            return 'bright_yellow'
        else:
            return 'bright_cyan'
    elif metric == 'revenue_growth':
        if value > 20:
            return 'bold bright_green'
        elif value > 15:
            return 'bright_green'
        elif value > 12:
            return 'bright_yellow'
        else:
            return 'bright_cyan'
    elif metric == 'gross_margin':
        if value > 60:
            return 'bold bright_green'
        elif value > 50:
            return 'bright_green'
        elif value > 45:
            return 'bright_yellow'
        else:
            return 'bright_cyan'
    return 'white'

def display_screener_results(stocks):
    """Display semiconductor screener results with vibrant formatting."""

    # Header
    title = Text("SEMICONDUCTOR STOCK SCREENER", style="bold bright_magenta on black")
    console.print(Align.center(title))
    console.print()

    # Screening criteria panel
    criteria_text = (
        f"[bold bright_white]Screening Criteria:[/bold bright_white]\n"
        f"[bold bright_green]✓[/bold bright_green] [bright_green]PE Ratio < 30[/bright_green]\n"
        f"[bold bright_green]✓[/bold bright_green] [bright_green]Revenue Growth > 10% YoY[/bright_green]\n"
        f"[bold bright_green]✓[/bold bright_green] [bright_green]Gross Margin > 40%[/bright_green]\n\n"
        f"[bold bright_white]Analysis Date:[/bold bright_white] {datetime.now().strftime('%B %d, %Y')}\n"
        f"[bold bright_white]Total Stocks Analyzed:[/bold bright_white] [bold bright_cyan]{len(stocks)}[/bold bright_cyan]"
    )
    criteria_panel = Panel(criteria_text, border_style="bright_magenta", style="on black")
    console.print(criteria_panel)
    console.print()

    # Filter stocks and add scores
    qualified_stocks = []
    for stock in stocks:
        stock['value_score'] = calculate_value_score(stock)
        if meets_criteria(stock):
            qualified_stocks.append(stock)

    # Sort by value score (highest first)
    qualified_stocks.sort(key=lambda x: x['value_score'], reverse=True)

    # Summary stats
    console.print("[bold bright_magenta]📊 SCREENING RESULTS[/bold bright_magenta]\n")

    summary_text = (
        f"[bold bright_white]Stocks Meeting All Criteria:[/bold bright_white] [bold bright_green]{len(qualified_stocks)}/20[/bold bright_green]\n"
        f"[bold bright_white]Top Pick Value Score:[/bold bright_white] [bold bright_green]{qualified_stocks[0]['value_score']}/100[/bold bright_green] ({qualified_stocks[0]['ticker']})\n"
        f"[bold bright_white]Average Value Score (Qualified):[/bold bright_white] [bold bright_yellow]{sum(s['value_score'] for s in qualified_stocks) / len(qualified_stocks):.1f}/100[/bold bright_yellow]"
    )
    summary_panel = Panel(summary_text, border_style="bright_cyan", style="on black")
    console.print(summary_panel)
    console.print()

    # Main results table
    if qualified_stocks:
        console.print("[bold bright_magenta]🏆 TOP VALUE PICKS - RANKED BY SCORE[/bold bright_magenta]\n")

        table = Table(show_header=True,
                     header_style="bold white on bright_magenta",
                     border_style="bright_magenta",
                     padding=(0, 1))

        table.add_column("Rank", style="bold bright_white", justify="center")
        table.add_column("Ticker", style="bold bright_yellow", justify="center")
        table.add_column("Company", style="bold bright_white")
        table.add_column("Price", style="bright_cyan", justify="right")
        table.add_column("PE Ratio", style="bright_white", justify="right")
        table.add_column("Growth %", style="bright_white", justify="right")
        table.add_column("Margin %", style="bright_white", justify="right")
        table.add_column("Score", style="bold bright_green", justify="center")

        for idx, stock in enumerate(qualified_stocks, 1):
            pe_color = get_metric_color('pe_ratio', stock['pe_ratio'])
            growth_color = get_metric_color('revenue_growth', stock['revenue_growth'])
            margin_color = get_metric_color('gross_margin', stock['gross_margin'])
            score_color = get_score_color(stock['value_score'])

            rank_display = f"[bold bright_green]#{idx}[/bold bright_green]" if idx <= 3 else f"#{idx}"

            table.add_row(
                rank_display,
                f"[bold bright_yellow]{stock['ticker']}[/bold bright_yellow]",
                stock['company'],
                f"[bright_cyan]${stock['price']:.2f}[/bright_cyan]",
                f"[{pe_color}]{stock['pe_ratio']:.1f}x[/{pe_color}]",
                f"[{growth_color}]{stock['revenue_growth']:.1f}%[/{growth_color}]",
                f"[{margin_color}]{stock['gross_margin']:.1f}%[/{margin_color}]",
                f"[{score_color}]{stock['value_score']:.0f}[/{score_color}]"
            )

        console.print(table)
        console.print()

        # Top 3 picks highlighted
        console.print("[bold bright_magenta]🎯 TOP 3 VALUE PICKS[/bold bright_magenta]\n")

        for idx, stock in enumerate(qualified_stocks[:3], 1):
            pick_text = (
                f"[bold bright_green]#{idx} - {stock['ticker']} ({stock['company']})[/bold bright_green]\n"
                f"[bold bright_white]Price:[/bold bright_white] [bright_cyan]${stock['price']:.2f}[/bright_cyan]  "
                f"[bold bright_white]PE:[/bold bright_white] [bright_green]{stock['pe_ratio']:.1f}x[/bright_green]  "
                f"[bold bright_white]Growth:[/bold bright_white] [bright_green]{stock['revenue_growth']:.1f}%[/bright_green]  "
                f"[bold bright_white]Margin:[/bold bright_white] [bright_green]{stock['gross_margin']:.1f}%[/bright_green]\n"
                f"[bold bright_green]Value Score: {stock['value_score']:.0f}/100[/bold bright_green]  "
                f"[bold bright_white]Market Cap:[/bold bright_white] [bright_cyan]${stock['market_cap']:.1f}B[/bright_cyan]  "
                f"[bold bright_white]Sector:[/bold bright_white] [bright_yellow]{stock['sector']}[/bright_yellow]"
            )
            pick_panel = Panel(pick_text, border_style="bright_green", style="on black")
            console.print(pick_panel)
            console.print()

    # All stocks table
    console.print("[bold bright_magenta]📈 ALL SEMICONDUCTOR STOCKS ANALYZED[/bold bright_magenta]\n")

    all_table = Table(show_header=True,
                     header_style="bold white on dark_magenta",
                     border_style="bright_magenta",
                     padding=(0, 1))

    all_table.add_column("Ticker", style="bold bright_white", justify="center")
    all_table.add_column("Company", style="white")
    all_table.add_column("Price", style="bright_cyan", justify="right")
    all_table.add_column("PE", style="bright_white", justify="right")
    all_table.add_column("Growth", style="bright_white", justify="right")
    all_table.add_column("Margin", style="bright_white", justify="right")
    all_table.add_column("Qualifies", style="bright_white", justify="center")
    all_table.add_column("Score", style="bright_white", justify="right")

    for stock in stocks:
        qualifies = "✓ YES" if meets_criteria(stock) else "✗ NO"
        qualifies_color = "[bold bright_green]✓ YES[/bold bright_green]" if meets_criteria(stock) else "[dim]✗ NO[/dim]"

        pe_color = get_metric_color('pe_ratio', stock['pe_ratio'])
        growth_color = get_metric_color('revenue_growth', stock['revenue_growth'])
        margin_color = get_metric_color('gross_margin', stock['gross_margin'])
        score_color = get_score_color(stock['value_score'])

        all_table.add_row(
            f"[bold bright_yellow]{stock['ticker']}[/bold bright_yellow]",
            stock['company'][:30],
            f"[bright_cyan]${stock['price']:.2f}[/bright_cyan]",
            f"[{pe_color}]{stock['pe_ratio']:.1f}[/{pe_color}]",
            f"[{growth_color}]{stock['revenue_growth']:.1f}%[/{growth_color}]",
            f"[{margin_color}]{stock['gross_margin']:.1f}%[/{margin_color}]",
            qualifies_color,
            f"[{score_color}]{stock['value_score']:.0f}[/{score_color}]"
        )

    console.print(all_table)
    console.print()

    # Investment insights
    console.print("[bold bright_magenta]💡 KEY INSIGHTS[/bold bright_magenta]\n")

    avg_pe = sum(s['pe_ratio'] for s in qualified_stocks) / len(qualified_stocks)
    avg_growth = sum(s['revenue_growth'] for s in qualified_stocks) / len(qualified_stocks)
    avg_margin = sum(s['gross_margin'] for s in qualified_stocks) / len(qualified_stocks)

    insights_text = (
        f"[bold bright_white]Qualified Stocks Average Metrics:[/bold bright_white]\n"
        f"[bright_green]• Average PE Ratio: [bold bright_green]{avg_pe:.1f}x[/bold bright_green] (lower is better)[/bright_green]\n"
        f"[bright_green]• Average Revenue Growth: [bold bright_green]{avg_growth:.1f}%[/bold bright_green] (strong growth)[/bright_green]\n"
        f"[bright_green]• Average Gross Margin: [bold bright_green]{avg_margin:.1f}%[/bold bright_green] (healthy profitability)[/bright_green]\n\n"
        f"[bold bright_yellow]Top Sector by Quality: [/bold bright_yellow]"
    )

    sector_scores = {}
    for stock in qualified_stocks:
        if stock['sector'] not in sector_scores:
            sector_scores[stock['sector']] = []
        sector_scores[stock['sector']].append(stock['value_score'])

    if sector_scores:
        best_sector = max(sector_scores.items(), key=lambda x: sum(x[1]) / len(x[1]))
        insights_text += f"[bold bright_green]{best_sector[0]}[/bold bright_green] (Avg Score: {sum(best_sector[1]) / len(best_sector[1]):.0f}/100)"

    insights_panel = Panel(insights_text, border_style="bright_magenta", style="on black")
    console.print(insights_panel)
    console.print()

    # Screening recommendations
    console.print("[bold bright_magenta]📋 SCREENING RECOMMENDATIONS[/bold bright_magenta]\n")

    if len(qualified_stocks) > 0:
        recommendations = (
            "[bold bright_green]✓ Strong Buy Candidates:[/bold bright_green]\n"
            f"  Stocks with score > 70: {len([s for s in qualified_stocks if s['value_score'] > 70])}\n\n"
            "[bold bright_yellow]⚠ Watch List:[/bold bright_yellow]\n"
            f"  Stocks with score 60-70: {len([s for s in qualified_stocks if 60 <= s['value_score'] <= 70])}\n\n"
            "[bold bright_red]✗ Threshold Failures:[/bold bright_red]\n"
            f"  Over PE 30: {len([s for s in stocks if s['pe_ratio'] >= 30])}\n"
            f"  Under 10% growth: {len([s for s in stocks if s['revenue_growth'] <= 10])}\n"
            f"  Under 40% margin: {len([s for s in stocks if s['gross_margin'] <= 40])}"
        )
    else:
        recommendations = "[dim]No stocks met all criteria in this analysis.[/dim]"

    rec_panel = Panel(recommendations, border_style="bright_magenta", style="on black")
    console.print(rec_panel)

def main():
    """Main execution function."""
    try:
        # Get stocks
        stocks = get_semiconductor_stocks()

        # Display results
        display_screener_results(stocks)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
