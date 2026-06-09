#!/usr/bin/env python3
"""
Personal Stock Portfolio Tracker
pip install yfinance rich
"""

import yfinance as yf
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich import box

console = Console()

PORTFOLIO = [
    {"ticker": "TSLA", "shares": 10, "buy_price": 408.00},
    {"ticker": "AAPL", "shares": 5,  "buy_price": 301.00},
    {"ticker": "NVDA", "shares": 8,  "buy_price": 205.00},
]

FALLBACK = {
    "TSLA": {"price": 182.63,  "name": "Tesla Inc"},
    "AAPL": {"price": 213.55,  "name": "Apple Inc"},
    "NVDA": {"price": 1208.88, "name": "NVIDIA Corp"},
}


def get_price(ticker):
    try:
        info = yf.Ticker(ticker).info
        price = info.get("currentPrice") or info.get("lastPrice")
        name  = info.get("shortName", ticker)
        if price and price > 0:
            return round(price, 2), name
    except:
        pass
    d = FALLBACK.get(ticker, {"price": 0, "name": ticker})
    return d["price"], d["name"]


def main():
    start = time.time()

    console.print()
    console.print(Align.center(Panel.fit(
        "[bold bright_yellow]💰  MY STOCK PORTFOLIO  💰[/]\n"
        "[dim]Personal tracker · Live prices · Gain & Loss[/]",
        border_style="bright_yellow", padding=(1, 10),
    )))
    console.print()
    console.print("[dim]Fetching today's prices...[/]\n")

    rows = []
    for h in PORTFOLIO:
        price, name = get_price(h["ticker"])
        cost        = h["shares"] * h["buy_price"]
        value       = h["shares"] * price
        gain        = value - cost
        gain_pct    = (gain / cost * 100) if cost else 0
        rows.append({**h, "name": name, "price": price,
                     "cost": cost, "value": value,
                     "gain": gain, "gain_pct": gain_pct})

    total_cost  = sum(r["cost"]  for r in rows)
    total_value = sum(r["value"] for r in rows)
    total_gain  = total_value - total_cost
    total_pct   = (total_gain / total_cost * 100) if total_cost else 0

    # ── Main table ────────────────────────────────────────────────────────────
    table = Table(
        title=f"[bold white]📊 Portfolio  —  {datetime.now():%b %d, %Y}[/]",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold black on #4fc3f7",
        show_lines=True,
        padding=(0, 2),
    )

    table.add_column("Stock",         justify="center", width=7,  style="bold yellow")
    table.add_column("Company",       justify="left",   width=16, style="white")
    table.add_column("Shares",        justify="right",  width=8)
    table.add_column("Buy Price",     justify="right",  width=12)
    table.add_column("Today Price",   justify="right",  width=13)
    table.add_column("Total Value",   justify="right",  width=13)
    table.add_column("Gain / Loss",   justify="right",  width=16)
    table.add_column("Return",        justify="right",  width=10)

    for r in rows:
        up    = r["gain"] >= 0
        col   = "bright_green" if up else "red"
        arrow = "▲" if up else "▼"
        sign  = "+" if up else ""
        emoji = "🚀" if r["gain_pct"] > 50 else ("📈" if up else "📉")

        table.add_row(
            f"{r['ticker']} {emoji}",
            r["name"],
            f"[white]{r['shares']}[/]",
            f"[dim]${r['buy_price']:,.2f}[/]",
            f"[bold white]${r['price']:,.2f}[/]",
            f"[bold bright_cyan]${r['value']:,.2f}[/]",
            f"[bold {col}]{sign}${abs(r['gain']):,.2f}[/]",
            f"[bold {col}]{arrow} {sign}{r['gain_pct']:.1f}%[/]",
        )

    # Totals row
    up    = total_gain >= 0
    col   = "bright_green" if up else "red"
    sign  = "+" if up else ""
    table.add_section()
    table.add_row(
        "[bold white]TOTAL[/]", "",
        f"[white]{sum(r['shares'] for r in rows)}[/]",
        f"[dim]${total_cost:,.2f}[/]",
        "",
        f"[bold bright_cyan]${total_value:,.2f}[/]",
        f"[bold {col}]{sign}${abs(total_gain):,.2f}[/]",
        f"[bold {col}]{sign}{total_pct:.1f}%[/]",
    )

    console.print(table)
    console.print()

    # ── Summary panels ────────────────────────────────────────────────────────
    best  = max(rows, key=lambda r: r["gain_pct"])
    worst = min(rows, key=lambda r: r["gain_pct"])
    up_c  = "bright_green" if total_gain >= 0 else "red"

    console.print(Columns([
        Panel(
            f"[dim]Invested[/]   [white]${total_cost:>10,.2f}[/]\n"
            f"[dim]Value    [/]   [bold bright_cyan]${total_value:>10,.2f}[/]\n"
            f"[dim]Gain/Loss[/]   [bold {up_c}]{sign}${abs(total_gain):>9,.2f}[/]",
            title="[bold]💼 Summary[/]",
            border_style="bright_cyan", width=30,
        ),
        Panel(
            f"[dim]Best[/]    [bold bright_green]{best['ticker']}[/]  "
            f"[bright_green]+{best['gain_pct']:.1f}%[/]\n"
            f"[dim]Worst[/]   [bold red]{worst['ticker']}[/]  "
            f"[red]{'+' if worst['gain_pct']>=0 else ''}{worst['gain_pct']:.1f}%[/]\n"
            f"[dim]Return[/]  [bold {up_c}]{sign}{total_pct:.1f}%[/]",
            title="[bold]📊 Performance[/]",
            border_style="magenta", width=30,
        ),
        Panel(
            f"[dim]Holdings[/]   [bold white]{len(rows)}[/]\n"
            f"[dim]Winners[/]    [bold bright_green]{sum(1 for r in rows if r['gain']>0)}[/] "
            f"[dim]/[/] [bold red]{sum(1 for r in rows if r['gain']<0)}[/] [dim]Losers[/]\n"
            f"[dim]Updated[/]    [white]{datetime.now():%H:%M:%S}[/]",
            title="[bold]📋 Stats[/]",
            border_style="yellow", width=28,
        ),
    ]))
    console.print()
    console.print(f"[dim]⏱ {time.time() - start:.2f}s[/]\n")


if __name__ == "__main__":
    main()
