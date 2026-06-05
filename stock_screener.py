#!/usr/bin/env python3
"""
Stock Screener — Revenue Growth > 20% | P/E < 30 | Market Cap > $10B
Uses sample data (live fetch blocked in this environment).
Run locally with: pip install yfinance rich && python stock_screener.py
"""

import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.columns import Columns
from rich.align import Align
import time

console = Console()

# ── Criteria ────────────────────────────────────────────────────────────────
CRITERIA = {
    "min_revenue_growth": 20.0,   # %
    "max_pe_ratio":       30.0,
    "min_market_cap_b":   10.0,   # $B
}

# ── Sample dataset (replace with yf.Ticker calls locally) ───────────────────
STOCKS = [
    {"ticker": "NVDA",  "name": "NVIDIA Corp",          "sector": "Technology",    "market_cap_b": 2850, "pe_ratio": 45.2, "rev_growth": 122.4, "gross_margin": 75.0, "fwd_pe": 32.1},
    {"ticker": "META",  "name": "Meta Platforms",        "sector": "Technology",    "market_cap_b":  1420, "pe_ratio": 24.8, "rev_growth":  27.1, "gross_margin": 81.5, "fwd_pe": 21.3},
    {"ticker": "ORCL",  "name": "Oracle Corp",           "sector": "Technology",    "market_cap_b":   530, "pe_ratio": 38.9, "rev_growth":  21.3, "gross_margin": 71.2, "fwd_pe": 24.7},
    {"ticker": "AMZN",  "name": "Amazon.com",            "sector": "Consumer Disc", "market_cap_b":  2100, "pe_ratio": 41.1, "rev_growth":  13.9, "gross_margin": 49.3, "fwd_pe": 31.8},
    {"ticker": "GOOGL", "name": "Alphabet Inc",          "sector": "Technology",    "market_cap_b":  2200, "pe_ratio": 21.4, "rev_growth":  15.1, "gross_margin": 57.1, "fwd_pe": 18.9},
    {"ticker": "PLTR",  "name": "Palantir Technologies", "sector": "Technology",    "market_cap_b":   220, "pe_ratio": 180.0,"rev_growth":  36.0, "gross_margin": 80.3, "fwd_pe": 95.0},
    {"ticker": "CRWD",  "name": "CrowdStrike Holdings",  "sector": "Cybersecurity", "market_cap_b":    95, "pe_ratio": 62.3, "rev_growth":  29.8, "gross_margin": 78.1, "fwd_pe": 48.2},
    {"ticker": "SNOW",  "name": "Snowflake Inc",         "sector": "Technology",    "market_cap_b":    45, "pe_ratio": None, "rev_growth":  26.3, "gross_margin": 69.8, "fwd_pe": 82.0},
    {"ticker": "DDOG",  "name": "Datadog Inc",           "sector": "Technology",    "market_cap_b":    38, "pe_ratio": 88.1, "rev_growth":  25.4, "gross_margin": 81.4, "fwd_pe": 55.3},
    {"ticker": "MSFT",  "name": "Microsoft Corp",        "sector": "Technology",    "market_cap_b":  3100, "pe_ratio": 35.6, "rev_growth":  17.6, "gross_margin": 70.1, "fwd_pe": 28.9},
    {"ticker": "TSM",   "name": "TSMC",                  "sector": "Semiconductors","market_cap_b":   900, "pe_ratio": 22.1, "rev_growth":  38.8, "gross_margin": 56.3, "fwd_pe": 19.4},
    {"ticker": "AVGO",  "name": "Broadcom Inc",          "sector": "Semiconductors","market_cap_b":   780, "pe_ratio": 28.4, "rev_growth":  44.0, "gross_margin": 64.8, "fwd_pe": 22.1},
    {"ticker": "APP",   "name": "AppLovin Corp",         "sector": "Ad Tech",       "market_cap_b":   115, "pe_ratio": 67.2, "rev_growth":  43.5, "gross_margin": 72.9, "fwd_pe": 39.8},
    {"ticker": "AXON",  "name": "Axon Enterprise",       "sector": "Public Safety",  "market_cap_b":    28, "pe_ratio": 92.3, "rev_growth":  33.8, "gross_margin": 61.2, "fwd_pe": 68.1},
    {"ticker": "CELH",  "name": "Celsius Holdings",      "sector": "Consumer Stapl","market_cap_b":    12, "pe_ratio": 24.6, "rev_growth":  18.2, "gross_margin": 50.1, "fwd_pe": 22.0},
]


def passes_screen(s):
    pe = s["pe_ratio"]
    return (
        s["rev_growth"]    > CRITERIA["min_revenue_growth"] and
        (pe is not None and pe < CRITERIA["max_pe_ratio"])  and
        s["market_cap_b"]  > CRITERIA["min_market_cap_b"]
    )


def color_rev_growth(val):
    if val >= 40:   return f"[bold bright_green]{val:.1f}%[/]"
    if val >= 20:   return f"[green]{val:.1f}%[/]"
    return         f"[red]{val:.1f}%[/]"

def color_pe(val):
    if val is None: return "[dim]N/A[/]"
    if val < 20:    return f"[bold bright_green]{val:.1f}[/]"
    if val < 30:    return f"[green]{val:.1f}[/]"
    if val < 50:    return f"[yellow]{val:.1f}[/]"
    return         f"[bold red]{val:.1f}[/]"

def color_market_cap(val):
    if val >= 1000: return f"[bold bright_cyan]${val:,.0f}B[/]"
    if val >= 100:  return f"[cyan]${val:,.0f}B[/]"
    return         f"[white]${val:.1f}B[/]"

def color_margin(val):
    if val >= 75:   return f"[bold bright_green]{val:.1f}%[/]"
    if val >= 55:   return f"[green]{val:.1f}%[/]"
    if val >= 40:   return f"[yellow]{val:.1f}%[/]"
    return         f"[red]{val:.1f}%[/]"

def pass_fail(stock):
    passed = passes_screen(stock)
    return "[bold bright_green]✓ PASS[/]" if passed else "[bold red]✗ FAIL[/]"

def score(s):
    """Simple composite score for sorting."""
    pe = s["pe_ratio"] or 999
    return (s["rev_growth"] * 2) + s["gross_margin"] - pe + (min(s["market_cap_b"], 500) / 50)


def build_universe_table(stocks):
    table = Table(
        title="[bold white]📊 Full Universe Screened[/]",
        box=box.ROUNDED,
        border_style="bright_blue",
        header_style="bold bright_white on #1a1a2e",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Ticker",        style="bold yellow",   justify="center", width=7)
    table.add_column("Company",       style="white",         justify="left",   width=22)
    table.add_column("Sector",        style="dim white",     justify="left",   width=14)
    table.add_column("Mkt Cap",                              justify="right",  width=10)
    table.add_column("Rev Growth",                           justify="right",  width=12)
    table.add_column("P/E",                                  justify="right",  width=8)
    table.add_column("Fwd P/E",                              justify="right",  width=9)
    table.add_column("Gross Margin",                         justify="right",  width=13)
    table.add_column("Screen",                               justify="center", width=9)

    for s in sorted(stocks, key=score, reverse=True):
        table.add_row(
            s["ticker"],
            s["name"],
            s["sector"],
            color_market_cap(s["market_cap_b"]),
            color_rev_growth(s["rev_growth"]),
            color_pe(s["pe_ratio"]),
            color_pe(s["fwd_pe"]),
            color_margin(s["gross_margin"]),
            pass_fail(s),
        )
    return table


def build_results_table(stocks):
    table = Table(
        title="[bold bright_green]🏆 Stocks Passing All 3 Criteria[/]",
        box=box.DOUBLE_EDGE,
        border_style="bright_green",
        header_style="bold black on bright_green",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("Rank",          justify="center", width=6,  style="bold bright_yellow")
    table.add_column("Ticker",        justify="center", width=7,  style="bold bright_white")
    table.add_column("Company",       justify="left",   width=24, style="white")
    table.add_column("Mkt Cap",       justify="right",  width=10)
    table.add_column("Rev Growth ↑",  justify="right",  width=13)
    table.add_column("P/E ↓",         justify="right",  width=8)
    table.add_column("Gross Margin",  justify="right",  width=13)
    table.add_column("Score",         justify="center", width=8)

    passed = [s for s in stocks if passes_screen(s)]
    passed.sort(key=score, reverse=True)

    for i, s in enumerate(passed, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"#{i}")
        sc = score(s)
        score_color = "bright_green" if sc > 80 else "green" if sc > 50 else "yellow"
        table.add_row(
            medal,
            s["ticker"],
            s["name"],
            color_market_cap(s["market_cap_b"]),
            color_rev_growth(s["rev_growth"]),
            color_pe(s["pe_ratio"]),
            color_margin(s["gross_margin"]),
            f"[bold {score_color}]{sc:.0f}[/]",
        )
    return table, len(passed)


def build_summary_panels(stocks):
    passed  = [s for s in stocks if passes_screen(s)]
    failed  = [s for s in stocks if not passes_screen(s)]
    avg_rg  = sum(s["rev_growth"] for s in passed) / len(passed) if passed else 0
    avg_pe  = sum(s["pe_ratio"] for s in passed if s["pe_ratio"]) / len(passed) if passed else 0

    panels = []

    p1 = Panel(
        f"[bold bright_green]{len(passed)}[/] [white]passed[/]\n"
        f"[bold red]{len(failed)}[/] [white]failed[/]\n"
        f"[dim]{len(stocks)} total screened[/]",
        title="[bold]Results[/]",
        border_style="bright_cyan",
        width=22,
    )
    p2 = Panel(
        f"Rev Growth [bold bright_green]>{CRITERIA['min_revenue_growth']:.0f}%[/]\n"
        f"P/E Ratio  [bold bright_green]<{CRITERIA['max_pe_ratio']:.0f}[/]\n"
        f"Mkt Cap    [bold bright_green]>${CRITERIA['min_market_cap_b']:.0f}B[/]",
        title="[bold]Criteria[/]",
        border_style="yellow",
        width=26,
    )
    p3 = Panel(
        f"Avg Rev Growth [bold bright_green]{avg_rg:.1f}%[/]\n"
        f"Avg P/E Ratio  [bold bright_green]{avg_pe:.1f}x[/]\n"
        f"Screened       [bold white]{datetime.now():%H:%M:%S}[/]",
        title="[bold]Averages[/]",
        border_style="magenta",
        width=28,
    )
    return Columns([p1, p2, p3], equal=False, expand=False)


def run_screener():
    console.print()
    console.print(Align.center(
        Panel.fit(
            "[bold bright_yellow]⚡ STOCK SCREENER ⚡[/]\n"
            "[dim white]Revenue Growth · P/E Ratio · Market Cap[/]",
            border_style="bright_yellow",
            padding=(1, 6),
        )
    ))
    console.print()

    # Simulate scanning animation
    with Progress(
        SpinnerColumn(spinner_name="dots12", style="bright_cyan"),
        TextColumn("[bright_cyan]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Scanning universe...", total=len(STOCKS))
        for s in STOCKS:
            progress.update(task, advance=1, description=f"Analyzing [yellow]{s['ticker']}[/]...")
            time.sleep(0.08)

    console.print(build_summary_panels(STOCKS))
    console.print()
    console.print(build_universe_table(STOCKS))
    console.print()

    results_table, n = build_results_table(STOCKS)
    console.print(results_table)
    console.print()

    if n == 0:
        console.print(Panel("[bold red]No stocks passed all criteria.[/]", border_style="red"))
    else:
        console.print(Panel(
            f"[bold bright_green]{n} stock{'s' if n > 1 else ''} passed all screening criteria.[/]\n"
            "[dim]Score = (Rev Growth × 2) + Gross Margin − P/E + size bonus[/]",
            border_style="bright_green",
            title="[bold]✓ Screen Complete[/]",
        ))
    console.print()


if __name__ == "__main__":
    run_screener()
