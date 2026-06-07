#!/usr/bin/env python3
"""
Stock Portfolio Sector Breakdown with Pie Chart
pip install yfinance matplotlib rich
"""

import yfinance as yf
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich import box

console = Console()

# ── Portfolio ────────────────────────────────────────────────────────────────
PORTFOLIO = [
    {"ticker": "NVDA", "shares": 10,  "entry_price": 875.00},
    {"ticker": "AAPL", "shares": 5,   "entry_price": 120.00},
    {"ticker": "AVGO", "shares": 10,  "entry_price": 130.00},
]

# Fallback data if yfinance fails
FALLBACK_DATA = {
    "NVDA": {"sector": "Semiconductors", "price": 1208.88, "name": "NVIDIA Corp"},
    "AAPL": {"sector": "Consumer Electronics", "price": 213.55, "name": "Apple Inc"},
    "AVGO": {"sector": "Semiconductors", "price": 1842.75, "name": "Broadcom Inc"},
}

# Color palette for sectors
SECTOR_COLORS = {
    "Semiconductors":       "#FF6B6B",
    "Consumer Electronics": "#4ECDC4",
    "Technology":           "#45B7D1",
    "Communication":        "#96CEB4",
    "Financials":           "#FFEAA7",
    "Healthcare":           "#DDA0DD",
    "Industrials":          "#F7B731",
    "Consumer":             "#A29BFE",
    "Energy":               "#FD79A8",
    "Materials":            "#FDCB6E",
}


def fetch_stock_info(ticker: str) -> dict:
    """Fetch sector and current price from yfinance."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        sector = info.get("sector", "Unknown")
        price = info.get("currentPrice") or info.get("lastPrice")
        name = info.get("shortName", ticker)

        if price and price > 0:
            return {"sector": sector, "price": round(price, 2), "name": name}
    except Exception as e:
        console.print(f"  [yellow]⚠ Could not fetch {ticker}: {str(e)[:40]}[/]")

    # Fallback
    if ticker in FALLBACK_DATA:
        return FALLBACK_DATA[ticker]

    return {"sector": "Unknown", "price": 0, "name": ticker}


def build_portfolio_table(holdings: list[dict]) -> Table:
    """Display holdings with current values."""
    table = Table(
        title="[bold bright_white]📊 Your Holdings[/]",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold black on #4fc3f7",
        show_lines=True,
        padding=(0, 1),
    )

    table.add_column("Ticker",        justify="center", width=8, style="bold yellow")
    table.add_column("Company",       justify="left",   width=20, style="white")
    table.add_column("Sector",        justify="left",   width=20, style="cyan")
    table.add_column("Shares",        justify="right",  width=8)
    table.add_column("Entry Price",   justify="right",  width=12)
    table.add_column("Current Price", justify="right",  width=14)
    table.add_column("Position Value",justify="right",  width=14)

    for h in holdings:
        entry_val = h["shares"] * h["entry_price"]
        current_val = h["shares"] * h["current_price"]
        gain_loss = current_val - entry_val
        gain_pct = (gain_loss / entry_val) * 100 if entry_val else 0

        color = "bright_green" if gain_loss >= 0 else "red"
        sign = "+" if gain_loss >= 0 else ""

        table.add_row(
            f"[bold yellow]{h['ticker']}[/]",
            h["name"][:18],
            h["sector"],
            f"[white]{h['shares']:,.0f}[/]",
            f"[dim]${h['entry_price']:,.2f}[/]",
            f"[bold bright_white]${h['current_price']:,.2f}[/]",
            f"[bold {color}]${current_val:,.2f}[/] ({sign}{gain_pct:.1f}%)",
        )

    return table


def build_sector_summary(sector_values: dict, total_value: float) -> Table:
    """Display sector allocation summary."""
    table = Table(
        title="[bold bright_white]🎯 Sector Breakdown[/]",
        box=box.ROUNDED,
        border_style="bright_magenta",
        header_style="bold black on #e91e63",
        show_lines=True,
        padding=(0, 1),
    )

    table.add_column("Sector",          justify="left",  width=24, style="cyan")
    table.add_column("Total Value",     justify="right", width=14)
    table.add_column("% of Portfolio",  justify="right", width=14)
    table.add_column("Allocation",      justify="left",  width=40)

    for sector in sorted(sector_values.keys(),
                        key=lambda s: sector_values[s],
                        reverse=True):
        value = sector_values[sector]
        pct = (value / total_value) * 100
        bars = int(pct * 2)

        color = SECTOR_COLORS.get(sector, "#CCCCCC")
        table.add_row(
            sector,
            f"[bold bright_cyan]${value:,.2f}[/]",
            f"[bold bright_yellow]{pct:.1f}%[/]",
            f"[{color}]{'█' * bars}{'░' * (50 - bars)}[/]",
        )

    return table


def main():
    console.print()
    console.print(Align.center(Panel.fit(
        "[bold bright_yellow]📈  SECTOR BREAKDOWN ANALYZER  📈[/]\n"
        "[dim]Analyze your portfolio by sector[/]",
        border_style="bright_yellow",
        padding=(1, 8),
    )))
    console.print()

    # Fetch current prices and sectors
    console.print("[dim]Fetching real-time data...[/]\n")
    holdings = []

    for h in PORTFOLIO:
        info = fetch_stock_info(h["ticker"])
        holding = {
            **h,
            "name": info["name"],
            "sector": info["sector"],
            "current_price": info["price"],
        }
        holdings.append(holding)
        console.print(
            f"  [green]✓[/] {h['ticker']:6} | {info['sector']:20} | "
            f"${info['price']:>10,.2f}"
        )

    console.print()

    # Display holdings table
    console.print(build_portfolio_table(holdings))
    console.print()

    # Calculate sector totals
    sector_values = defaultdict(float)
    total_value = 0

    for h in holdings:
        position_value = h["shares"] * h["current_price"]
        sector_values[h["sector"]] += position_value
        total_value += position_value

    # Display sector summary
    console.print(build_sector_summary(dict(sector_values), total_value))
    console.print()

    # Portfolio stats
    entry_total = sum(h["shares"] * h["entry_price"] for h in holdings)
    total_gain = total_value - entry_total
    total_pct = (total_gain / entry_total) * 100 if entry_total else 0

    color = "bright_green" if total_gain >= 0 else "red"
    sign = "+" if total_gain >= 0 else ""

    stats = Columns([
        Panel(
            f"[dim]Invested[/]  [white]${entry_total:>12,.2f}[/]\n"
            f"[dim]Value    [/]  [bold bright_cyan]${total_value:>12,.2f}[/]\n"
            f"[dim]Gain/Loss[/]  [bold {color}]{sign}${abs(total_gain):>11,.2f}[/]",
            title="[bold]💼 Portfolio Stats[/]",
            border_style="bright_cyan",
            width=36,
        ),
        Panel(
            f"[dim]Total Return[/]  [bold {color}]{sign}{total_pct:.2f}%[/]\n"
            f"[dim]Holdings[/]      [bold white]{len(holdings)}[/]\n"
            f"[dim]Sectors[/]       [bold bright_yellow]{len(sector_values)}[/]",
            title="[bold]📊 Summary[/]",
            border_style="magenta",
            width=32,
        ),
    ])
    console.print(stats)
    console.print()

    # ── Create pie chart ────────────────────────────────────────────────────
    sectors = list(sector_values.keys())
    values = list(sector_values.values())
    colors = [SECTOR_COLORS.get(s, "#CCCCCC") for s in sectors]

    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#1a1a1a")
    ax.set_facecolor("#1a1a1a")

    wedges, texts, autotexts = ax.pie(
        values,
        labels=sectors,
        colors=colors,
        autopct=lambda pct: f"{pct:.1f}%\n(${pct/100*total_value:,.0f})",
        startangle=90,
        textprops={
            "color": "#ffffff",
            "fontsize": 10,
            "weight": "bold",
        },
        wedgeprops={"edgecolor": "#1a1a1a", "linewidth": 2},
    )

    # Style percentage text
    for autotext in autotexts:
        autotext.set_color("#ffffff")
        autotext.set_fontsize(9)
        autotext.set_weight("bold")

    # Title
    ax.set_title(
        f"Portfolio Sector Breakdown\nTotal Value: ${total_value:,.2f}",
        color="#ffffff",
        fontsize=14,
        weight="bold",
        pad=20,
    )

    # Legend
    ax.legend(
        wedges,
        [f"{s}: ${sector_values[s]:,.2f}" for s in sectors],
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=10,
        frameon=True,
        facecolor="#2a2a2a",
        edgecolor="#ffffff",
        labelcolor="#ffffff",
    )

    plt.tight_layout()

    # Save the chart
    filename = "/home/user/claude-test/sector_breakdown_chart.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="#1a1a1a")
    console.print(f"[green]✓ Chart saved to[/] [bold]{filename}[/]")
    console.print()

    plt.show()


if __name__ == "__main__":
    main()
