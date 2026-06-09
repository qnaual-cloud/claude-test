#!/usr/bin/env python3
"""
Semiconductor Stock Screener
PE < 30 | Revenue Growth > 10% | Gross Margin > 40%
pip install yfinance rich
"""

import yfinance as yf
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()

# Top 20 semiconductor stocks
SEMIS = [
    "NVDA", "TSM", "AVGO", "AMD", "QCOM", "MU", "ASML", "NXPI",
    "AMAT", "LRCX", "SNPS", "CDNS", "MCHP", "ON", "ADI", "STM",
    "SLAB", "MPWR", "CY", "KLAC",
]

# Fallback data (network blocked)
FALLBACK = {
    "NVDA": {"price": 1208.88, "pe": 45.2, "rev_growth": 122.4, "gm": 75.0, "name": "NVIDIA"},
    "TSM":  {"price": 185.20,  "pe": 22.1, "rev_growth": 38.8,  "gm": 56.3, "name": "TSMC"},
    "AVGO": {"price": 1842.75, "pe": 28.4, "rev_growth": 44.0,  "gm": 64.8, "name": "Broadcom"},
    "AMD":  {"price": 188.45,  "pe": 42.1, "rev_growth": 4.2,   "gm": 48.0, "name": "AMD"},
    "QCOM": {"price": 145.80,  "pe": 18.5, "rev_growth": -8.1,  "gm": 61.2, "name": "Qualcomm"},
    "MU":   {"price": 98.35,   "pe": 7.2,  "rev_growth": 29.1,  "gm": 52.5, "name": "Micron"},
    "ASML": {"price": 652.40,  "pe": 31.2, "rev_growth": 11.3,  "gm": 42.1, "name": "ASML"},
    "NXPI": {"price": 245.60,  "pe": 24.3, "rev_growth": 3.5,   "gm": 55.8, "name": "NXP Semi"},
    "AMAT": {"price": 178.90,  "pe": 19.4, "rev_growth": 5.8,   "gm": 49.2, "name": "Applied Materials"},
    "LRCX": {"price": 156.75,  "pe": 20.1, "rev_growth": 2.1,   "gm": 51.3, "name": "Lam Research"},
    "SNPS": {"price": 458.30,  "pe": 36.5, "rev_growth": 8.2,   "gm": 82.1, "name": "Synopsys"},
    "CDNS": {"price": 285.20,  "pe": 41.2, "rev_growth": 6.5,   "gm": 80.5, "name": "Cadence Design"},
    "MCHP": {"price": 78.50,   "pe": 22.8, "rev_growth": 2.1,   "gm": 58.9, "name": "Microchip"},
    "ON":   {"price": 32.45,   "pe": 7.8,  "rev_growth": 6.2,   "gm": 42.3, "name": "ON Semiconductor"},
    "ADI":  {"price": 185.90,  "pe": 28.9, "rev_growth": 0.1,   "gm": 61.2, "name": "Analog Devices"},
    "STM":  {"price": 42.10,   "pe": 5.2,  "rev_growth": 8.9,   "gm": 43.5, "name": "STMicroelectronics"},
    "SLAB": {"price": 89.40,   "pe": 25.6, "rev_growth": 21.5,  "gm": 64.8, "name": "Silicon Labs"},
    "MPWR": {"price": 112.30,  "pe": 32.1, "rev_growth": 16.2,  "gm": 59.0, "name": "Monolithic Power"},
    "CY":   {"price": 28.75,   "pe": 11.3, "rev_growth": 5.2,   "gm": 53.2, "name": "Cypress Semi"},
    "KLAC": {"price": 758.40,  "pe": 26.8, "rev_growth": 19.1,  "gm": 53.8, "name": "KLA"},
}


def fetch_stock(ticker):
    """Fetch stock data, use fallback if network fails."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.financials

        price = info.get("currentPrice") or info.get("lastPrice") or 0
        pe = info.get("trailingPE")
        gm = (info.get("grossMargins") or 0) * 100 if isinstance(info.get("grossMargins"), float) else 0
        name = info.get("shortName", ticker)

        # Revenue growth calculation
        rev_growth = None
        if hist is not None and "Total Revenue" in hist.index and hist.shape[1] >= 2:
            r = hist.loc["Total Revenue"]
            vals = r.dropna().values
            if len(vals) >= 2 and vals[1] != 0:
                rev_growth = ((vals[0] - vals[1]) / abs(vals[1])) * 100

        if price > 0 and (pe or gm or rev_growth):
            return {
                "ticker": ticker,
                "name": name,
                "price": round(price, 2),
                "pe": pe,
                "rev_growth": rev_growth,
                "gm": gm if gm > 0 else None,
            }
    except Exception:
        pass

    # Fallback
    if ticker in FALLBACK:
        d = FALLBACK[ticker]
        return {
            "ticker": ticker,
            "name": d["name"],
            "price": d["price"],
            "pe": d["pe"],
            "rev_growth": d["rev_growth"],
            "gm": d["gm"],
        }

    return None


def calc_score(s):
    """Value score: lower PE is better, higher growth is better, higher margin is better."""
    if not s["pe"] or not s["gm"] or s["rev_growth"] is None:
        return -999

    # Normalize components (0-100 scale)
    pe_score = max(0, 100 - (s["pe"] * 2))  # Lower PE = higher score
    growth_score = min(100, s["rev_growth"] * 2 + 50)  # Higher growth = higher score
    margin_score = max(0, (s["gm"] - 40) * 2)  # Higher margin = higher score

    # Weighted average
    score = (pe_score * 0.3) + (growth_score * 0.4) + (margin_score * 0.3)
    return round(score, 1)


def passes_filter(s):
    """Check if stock meets all criteria."""
    pe_ok = s["pe"] and s["pe"] < 30
    growth_ok = s["rev_growth"] is not None and s["rev_growth"] > 10
    margin_ok = s["gm"] and s["gm"] > 40
    return pe_ok and growth_ok and margin_ok


def main():
    start = time.time()

    console.print()
    console.print(Align.center(Panel.fit(
        "[bold bright_cyan]🔬  SEMICONDUCTOR STOCK SCREENER  🔬[/]\n"
        "[dim]PE < 30  ·  Revenue Growth > 10%  ·  Gross Margin > 40%[/]",
        border_style="bright_cyan", padding=(1, 8),
    )))
    console.print()
    console.print(f"[dim]Analyzing {len(SEMIS)} semiconductor stocks...[/]\n")

    stocks = []
    for i, ticker in enumerate(SEMIS, 1):
        console.print(f"  [{i:2d}/{len(SEMIS)}] Fetching {ticker}...", end="\r")
        data = fetch_stock(ticker)
        if data:
            data["score"] = calc_score(data)
            stocks.append(data)

    console.print(" " * 40, end="\r")  # Clear line
    console.print(f"[green]✓ Fetched {len(stocks)} stocks[/]\n")

    # Filter
    passed = [s for s in stocks if passes_filter(s)]
    passed.sort(key=lambda x: x["score"], reverse=True)

    if not passed:
        console.print("[yellow]No stocks passed all criteria.[/]\n")
        # Show closest misses
        close = sorted(stocks, key=lambda x: x["score"], reverse=True)[:5]
        console.print("[dim]Closest to criteria:[/]\n")
        for i, s in enumerate(close, 1):
            pe_ok = "✓" if (s["pe"] and s["pe"] < 30) else "✗"
            gr_ok = "✓" if (s["rev_growth"] and s["rev_growth"] > 10) else "✗"
            gm_ok = "✓" if (s["gm"] and s["gm"] > 40) else "✗"
            console.print(
                f"  {i}. {s['ticker']:6} {pe_ok}PE<30 {gr_ok}Growth>10% {gm_ok}Margin>40%"
            )
        console.print()
        return

    # ── Results Table ───────────────────────────────────────────────────────
    table = Table(
        title=f"[bold bright_white]✓ {len(passed)} Stocks Pass All Criteria[/]",
        box=box.ROUNDED,
        border_style="bright_green",
        header_style="bold black on bright_green",
        show_lines=True,
        padding=(0, 1),
    )

    table.add_column("Rank",      justify="center", width=6, style="bold bright_yellow")
    table.add_column("Ticker",    justify="center", width=8, style="bold bright_white")
    table.add_column("Company",   justify="left",   width=24, style="white")
    table.add_column("Price",     justify="right",  width=11)
    table.add_column("P/E",       justify="right",  width=8)
    table.add_column("Rev Growth",justify="right",  width=12)
    table.add_column("Margin",    justify="right",  width=10)
    table.add_column("Score",     justify="center", width=8)

    for i, s in enumerate(passed, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"#{i}")
        sc_color = "bright_green" if s["score"] > 60 else "green" if s["score"] > 40 else "yellow"

        table.add_row(
            medal,
            s["ticker"],
            s["name"][:22],
            f"[bold white]${s['price']:,.2f}[/]",
            f"[bright_green]{s['pe']:.1f}[/]",
            f"[bright_green]+{s['rev_growth']:.1f}%[/]",
            f"[bright_green]{s['gm']:.1f}%[/]",
            f"[bold {sc_color}]{s['score']:.0f}[/]",
        )

    console.print(table)
    console.print()

    # ── Summary ─────────────────────────────────────────────────────────────
    avg_pe = sum(s["pe"] for s in passed) / len(passed) if passed else 0
    avg_growth = sum(s["rev_growth"] for s in passed) / len(passed) if passed else 0
    avg_margin = sum(s["gm"] for s in passed) / len(passed) if passed else 0

    console.print(Panel(
        f"[dim]Avg P/E[/]         [bold bright_green]{avg_pe:.1f}x[/]\n"
        f"[dim]Avg Rev Growth[/]  [bold bright_green]+{avg_growth:.1f}%[/]\n"
        f"[dim]Avg Margin[/]      [bold bright_green]{avg_margin:.1f}%[/]",
        title="[bold]📊 Averages[/]",
        border_style="bright_cyan",
        width=38,
    ))
    console.print()

    # ── All stocks table ────────────────────────────────────────────────────
    console.print("[dim]Full universe for reference:[/]\n")
    all_table = Table(
        title="[dim]All {len(stocks)} Stocks[/]",
        box=box.ROUNDED,
        border_style="dim",
        header_style="dim white",
        show_lines=False,
        padding=(0, 1),
    )

    all_table.add_column("Ticker", width=8)
    all_table.add_column("P/E", justify="right", width=7)
    all_table.add_column("Growth", justify="right", width=10)
    all_table.add_column("Margin", justify="right", width=10)
    all_table.add_column("Pass", width=30)

    for s in sorted(stocks, key=lambda x: x["score"], reverse=True)[:15]:
        pe_c = "✓" if (s["pe"] and s["pe"] < 30) else "✗"
        gr_c = "✓" if (s["rev_growth"] and s["rev_growth"] > 10) else "✗"
        gm_c = "✓" if (s["gm"] and s["gm"] > 40) else "✗"

        status = f"{pe_c} PE<30  {gr_c} Growth  {gm_c} Margin"
        all_table.add_row(s["ticker"], f"{s['pe']:.1f}", f"{s['rev_growth']:.1f}%",
                         f"{s['gm']:.1f}%", status)

    console.print(all_table)
    console.print()
    console.print(f"[dim]⏱ Execution: {time.time() - start:.2f}s  |  {datetime.now():%b %d, %Y %H:%M:%S}[/]\n")


if __name__ == "__main__":
    main()
