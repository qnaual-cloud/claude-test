#!/usr/bin/env python3
"""
Quick Rebalancing Alert — Table Only (No Charts)
Fast execution for real-time monitoring
pip install yfinance rich
"""

import yfinance as yf
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

PORTFOLIO = [
    {"ticker": "NVDA", "shares": 10,  "entry": 205.00},
    {"ticker": "AAPL", "shares": 5,   "entry": 307.00},
    {"ticker": "AVGO", "shares": 10,  "entry": 385.00},
]

TARGET = {
    "Semiconductors":       40.0,
    "Consumer Electronics": 30.0,
    "Infrastructure":       30.0,
}

THRESHOLD = 5.0

FALLBACK = {
    "NVDA": {"sector": "Semiconductors",       "price": 1208.88},
    "AAPL": {"sector": "Consumer Electronics", "price": 213.55},
    "AVGO": {"sector": "Semiconductors",       "price": 1842.75},
}


def get_price(ticker):
    try:
        info = yf.Ticker(ticker).info
        if price := (info.get("currentPrice") or info.get("lastPrice")):
            if price > 0:
                return price, info.get("sector", "Unknown")
    except:
        pass
    data = FALLBACK.get(ticker)
    return data["price"], data["sector"] if data else (0, "Unknown")


def run():
    start = time.time()
    console.print("\n[dim]Fetching prices...[/]\n")

    # Fetch data
    holdings = []
    sector_vals = {}
    total = 0

    for h in PORTFOLIO:
        price, sector = get_price(h["ticker"])
        val = h["shares"] * price
        total += val
        holdings.append({"ticker": h["ticker"], "sector": sector, "val": val})
        sector_vals[sector] = sector_vals.get(sector, 0) + val

    # Build rebalance table
    table = Table(
        title="[bold bright_white]⚖️  REBALANCING ALERT[/]",
        box=box.ROUNDED,
        border_style="bright_yellow",
        header_style="bold black on bright_yellow",
        show_lines=True,
        padding=(0, 1),
    )

    table.add_column("Sector",          justify="left",   width=24, style="cyan")
    table.add_column("Current %",       justify="right",  width=12)
    table.add_column("Target %",        justify="right",  width=11)
    table.add_column("Drift %",         justify="right",  width=11)
    table.add_column("Current $",       justify="right",  width=13)
    table.add_column("Flag",            justify="center", width=6)
    table.add_column("Action",          justify="left",   width=32)

    flagged_count = 0

    for sector, target_pct in sorted(TARGET.items()):
        current_val = sector_vals.get(sector, 0)
        current_pct = (current_val / total * 100) if total else 0
        drift = current_pct - target_pct
        is_flagged = abs(drift) > THRESHOLD

        if is_flagged:
            flagged_count += 1

        flag = "[bold bright_red]🚩[/]" if is_flagged else "[dim]—[/]"

        if is_flagged:
            if drift > 0:
                action = f"[bold red]SELL ~${drift/100*total:,.0f}[/]"
            else:
                action = f"[bold yellow]BUY ~${abs(drift)/100*total:,.0f}[/]"
        else:
            action = "[dim green]✓ OK[/]"

        drift_color = "bright_red" if is_flagged else "bright_green" if abs(drift) < 2 else "yellow"
        drift_sign = "+" if drift >= 0 else ""

        table.add_row(
            f"[bold]{sector}[/]",
            f"[white]{current_pct:.1f}%[/]",
            f"[dim]{target_pct:.0f}%[/]",
            f"[bold {drift_color}]{drift_sign}{drift:.1f}%[/]",
            f"[bright_cyan]${current_val:,.2f}[/]",
            flag,
            action,
        )

    console.print(table)
    console.print()

    # Alert summary
    if flagged_count > 0:
        console.print(f"[bold bright_red]🚨 ALERT: {flagged_count} sector(s) out of balance[/]")
    else:
        console.print("[bold bright_green]✅ Portfolio balanced within ±5% threshold[/]")

    console.print(
        f"[dim]Total portfolio: ${total:,.2f}  |  "
        f"Execution: {time.time() - start:.2f}s  |  "
        f"{datetime.now():%b %d, %Y %H:%M:%S}[/]\n"
    )


if __name__ == "__main__":
    run()
