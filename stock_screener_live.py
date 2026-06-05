#!/usr/bin/env python3
"""
Live Stock Screener — Revenue Growth > 20% | P/E < 30 | Market Cap > $10B
pip install yfinance rich
"""

import yfinance as yf
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

console = Console()

CRITERIA = {"min_rev_growth": 20.0, "max_pe": 30.0, "min_mktcap_b": 10.0}

WATCHLIST = [
    "AAPL","MSFT","GOOGL","META","AMZN","NVDA","TSLA","AVGO","TSM",
    "ORCL","CRM","ADBE","PLTR","CRWD","DDOG","SNOW","APP","AXON",
    "AMD","QCOM","ASML","SAP","NOW","UBER","NET",
]

def fetch(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.financials
        mktcap  = info.get("marketCap", 0) / 1e9
        pe      = info.get("trailingPE")
        name    = info.get("shortName", ticker)
        sector  = info.get("sector", "—")
        gm      = (info.get("grossMargins") or 0) * 100
        fwd_pe  = info.get("forwardPE")

        rev_growth = None
        if hist is not None and "Total Revenue" in hist.index and hist.shape[1] >= 2:
            r = hist.loc["Total Revenue"]
            vals = r.dropna().values
            if len(vals) >= 2 and vals[1] != 0:
                rev_growth = ((vals[0] - vals[1]) / abs(vals[1])) * 100

        return {
            "ticker": ticker, "name": name, "sector": sector,
            "market_cap_b": mktcap, "pe_ratio": pe, "fwd_pe": fwd_pe,
            "rev_growth": rev_growth, "gross_margin": gm,
        }
    except Exception:
        return None

def passes(s):
    pe = s["pe_ratio"]
    rg = s["rev_growth"]
    return (
        rg is not None and rg > CRITERIA["min_rev_growth"] and
        pe is not None and pe < CRITERIA["max_pe"] and
        s["market_cap_b"] > CRITERIA["min_mktcap_b"]
    )

def c_rg(v):
    if v is None: return "[dim]N/A[/]"
    if v >= 40:   return f"[bold bright_green]{v:.1f}%[/]"
    if v >= 20:   return f"[green]{v:.1f}%[/]"
    return               f"[red]{v:.1f}%[/]"

def c_pe(v):
    if v is None: return "[dim]N/A[/]"
    if v < 20:    return f"[bold bright_green]{v:.1f}[/]"
    if v < 30:    return f"[green]{v:.1f}[/]"
    if v < 60:    return f"[yellow]{v:.1f}[/]"
    return               f"[bold red]{v:.1f}[/]"

def c_cap(v):
    if v >= 1000: return f"[bold bright_cyan]${v:,.0f}B[/]"
    if v >= 100:  return f"[cyan]${v:.0f}B[/]"
    return               f"[white]${v:.1f}B[/]"

def c_gm(v):
    if v >= 75:   return f"[bold bright_green]{v:.1f}%[/]"
    if v >= 50:   return f"[green]{v:.1f}%[/]"
    if v >= 30:   return f"[yellow]{v:.1f}%[/]"
    return               f"[red]{v:.1f}%[/]"

def score(s):
    rg = s["rev_growth"] or 0
    pe = s["pe_ratio"] or 999
    return rg * 2 + s["gross_margin"] - pe + min(s["market_cap_b"], 500) / 50

def main():
    console.print()
    console.print(Align.center(Panel.fit(
        "[bold bright_yellow]⚡  LIVE STOCK SCREENER  ⚡[/]\n"
        "[dim]Rev Growth >20%  ·  P/E <30  ·  Mkt Cap >$10B[/]",
        border_style="bright_yellow", padding=(1, 8),
    )))
    console.print()

    stocks = []
    with Progress(
        SpinnerColumn(style="bright_cyan"),
        TextColumn("[bright_cyan]{task.description}"),
        BarColumn(bar_width=30, style="bright_blue"),
        TextColumn("[dim]{task.completed}/{task.total}[/]"),
        console=console, transient=True,
    ) as prog:
        task = prog.add_task("Fetching live data...", total=len(WATCHLIST))
        for tkr in WATCHLIST:
            prog.update(task, advance=1, description=f"Fetching [yellow]{tkr}[/]...")
            data = fetch(tkr)
            if data:
                stocks.append(data)

    stocks.sort(key=score, reverse=True)
    passed = [s for s in stocks if passes(s)]

    # ── Summary panels ───────────────────────────────────────────────────────
    avg_rg = sum(s["rev_growth"] for s in passed if s["rev_growth"]) / max(len(passed),1)
    avg_pe = sum(s["pe_ratio"]   for s in passed if s["pe_ratio"])   / max(len(passed),1)
    console.print(Columns([
        Panel(f"[bold bright_green]{len(passed)}[/] passed\n[bold red]{len(stocks)-len(passed)}[/] failed\n[dim]{len(stocks)} fetched[/]",
              title="Results", border_style="bright_cyan", width=20),
        Panel(f"Rev Growth [bright_green]>{CRITERIA['min_rev_growth']:.0f}%[/]\nP/E Ratio  [bright_green]<{CRITERIA['max_pe']:.0f}[/]\nMkt Cap    [bright_green]>${CRITERIA['min_mktcap_b']:.0f}B[/]",
              title="Criteria", border_style="yellow", width=24),
        Panel(f"Avg Rev Growth [bright_green]{avg_rg:.1f}%[/]\nAvg P/E        [bright_green]{avg_pe:.1f}x[/]\nUpdated        [white]{datetime.now():%H:%M:%S}[/]",
              title="Stats", border_style="magenta", width=28),
    ]))
    console.print()

    # ── Full universe table ───────────────────────────────────────────────────
    univ = Table(title="[bold white]📊 Full Universe[/]", box=box.ROUNDED,
                 border_style="bright_blue", header_style="bold white on #1a1a2e",
                 show_lines=True, padding=(0,1))
    for col, kw in [("Ticker",{},), ("Company",{"width":22}), ("Sector",{"width":14,"style":"dim"}),
                     ("Mkt Cap",{"justify":"right"}), ("Rev Growth",{"justify":"right"}),
                     ("P/E",{"justify":"right","width":8}), ("Fwd P/E",{"justify":"right","width":8}),
                     ("Gross Margin",{"justify":"right"}), ("✓",{"justify":"center","width":6})]:
        univ.add_column(col, **kw)

    for s in stocks:
        ok = "[bold bright_green]✓[/]" if passes(s) else "[bold red]✗[/]"
        univ.add_row(
            f"[bold yellow]{s['ticker']}[/]", s["name"], s["sector"],
            c_cap(s["market_cap_b"]), c_rg(s["rev_growth"]),
            c_pe(s["pe_ratio"]), c_pe(s["fwd_pe"]), c_gm(s["gross_margin"]), ok,
        )
    console.print(univ)
    console.print()

    # ── Winners table ─────────────────────────────────────────────────────────
    if not passed:
        console.print(Panel("[bold red]No stocks passed all criteria.[/]", border_style="red"))
        return

    win = Table(title="[bold bright_green]🏆 Stocks Passing All Criteria[/]",
                box=box.DOUBLE_EDGE, border_style="bright_green",
                header_style="bold black on bright_green", show_lines=True, padding=(0,1))
    for col, kw in [("Rank",{"justify":"center","width":6,"style":"bold bright_yellow"}),
                     ("Ticker",{"justify":"center","width":7,"style":"bold bright_white"}),
                     ("Company",{"width":24}), ("Mkt Cap",{"justify":"right"}),
                     ("Rev Growth ↑",{"justify":"right"}), ("P/E ↓",{"justify":"right","width":8}),
                     ("Gross Margin",{"justify":"right"}), ("Score",{"justify":"center","width":7})]:
        win.add_column(col, **kw)

    for i, s in enumerate(sorted(passed, key=score, reverse=True), 1):
        medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i, f"#{i}")
        sc    = score(s)
        sc_c  = "bright_green" if sc > 80 else "green" if sc > 50 else "yellow"
        win.add_row(medal, s["ticker"], s["name"],
                    c_cap(s["market_cap_b"]), c_rg(s["rev_growth"]),
                    c_pe(s["pe_ratio"]), c_gm(s["gross_margin"]),
                    f"[bold {sc_c}]{sc:.0f}[/]")
    console.print(win)
    console.print()
    console.print(Panel(
        f"[bold bright_green]{len(passed)} stock{'s' if len(passed)>1 else ''} passed.[/]  "
        f"[dim]Score = (RevGrowth×2) + GrossMargin − P/E + size bonus[/]",
        border_style="bright_green", title="[bold]✓ Screen Complete[/]",
    ))
    console.print()

if __name__ == "__main__":
    main()
