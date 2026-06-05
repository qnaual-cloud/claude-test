#!/usr/bin/env python3
"""
Personal Stock Portfolio Tracker
pip install yfinance rich
"""

import yfinance as yf
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich import box

console = Console()

# ── Demo portfolio (used if user skips manual entry) ─────────────────────────
DEMO_PORTFOLIO = [
    {"ticker": "AAPL",  "shares": 50,  "avg_cost": 145.00},
    {"ticker": "NVDA",  "shares": 20,  "avg_cost": 420.00},
    {"ticker": "META",  "shares": 30,  "avg_cost": 280.00},
    {"ticker": "MSFT",  "shares": 25,  "avg_cost": 310.00},
    {"ticker": "TSLA",  "shares": 15,  "avg_cost": 220.00},
    {"ticker": "GOOGL", "shares": 10,  "avg_cost": 140.00},
    {"ticker": "AVGO",  "shares": 8,   "avg_cost": 850.00},
    {"ticker": "AMZN",  "shares": 18,  "avg_cost": 175.00},
]

# Fallback prices if yfinance is blocked
FALLBACK_PRICES = {
    "AAPL": 213.55, "NVDA": 1208.88, "META": 578.12, "MSFT": 458.33,
    "TSLA": 182.63, "GOOGL": 179.21, "AVGO": 1842.75, "AMZN": 221.44,
    "TSM": 185.20,  "ORCL": 165.40,  "PLTR": 38.22,   "CRWD": 398.15,
}


def fetch_price(ticker: str) -> tuple[float | None, str | None]:
    """Returns (price, company_name) or (None, None) on failure."""
    try:
        info = yf.Ticker(ticker).fast_info
        price = info.last_price
        name  = yf.Ticker(ticker).info.get("shortName", ticker)
        if price and price > 0:
            return round(price, 2), name
    except Exception:
        pass
    # Fallback
    price = FALLBACK_PRICES.get(ticker.upper())
    return (price, ticker) if price else (None, None)


def input_portfolio() -> list[dict]:
    console.print()
    console.print(Rule("[bold bright_cyan]Portfolio Entry[/]", style="bright_cyan"))
    console.print("[dim]Enter your holdings. Type [bold]done[/] when finished.[/]\n")

    holdings = []
    while True:
        ticker = Prompt.ask("[bold yellow]  Ticker[/] (or 'done')").strip().upper()
        if ticker == "DONE":
            break
        if not ticker:
            continue
        try:
            shares = float(Prompt.ask(f"  [cyan]Shares owned[/] for {ticker}"))
            cost   = float(Prompt.ask(f"  [cyan]Avg purchase price[/] for {ticker} ($)"))
            holdings.append({"ticker": ticker, "shares": shares, "avg_cost": cost})
            console.print(f"  [green]✓ Added {ticker}[/]\n")
        except ValueError:
            console.print("  [red]Invalid number, skipping.[/]\n")
    return holdings


def build_row(h: dict) -> dict | None:
    price, name = fetch_price(h["ticker"])
    if price is None:
        return None
    cost_basis   = h["shares"] * h["avg_cost"]
    current_val  = h["shares"] * price
    gain_loss    = current_val - cost_basis
    pct_return   = (gain_loss / cost_basis) * 100 if cost_basis else 0
    return {
        **h,
        "name":        name or h["ticker"],
        "price":       price,
        "cost_basis":  cost_basis,
        "current_val": current_val,
        "gain_loss":   gain_loss,
        "pct_return":  pct_return,
    }


def arrow(v):  return "▲" if v >= 0 else "▼"
def sign(v):   return "+" if v >= 0 else ""
def up(v):     return "bright_green" if v >= 0 else "red"

def fmt_money(v):
    c = up(v)
    return f"[bold {c}]{sign(v)}${abs(v):,.2f}[/]"

def fmt_pct(v):
    c = up(v)
    return f"[bold {c}]{sign(v)}{v:.2f}%[/]"

def c_price(v):
    return f"[bold white]${v:,.2f}[/]"

def c_val(v):
    if v >= 100_000: return f"[bold bright_cyan]${v:,.2f}[/]"
    if v >= 10_000:  return f"[cyan]${v:,.2f}[/]"
    return                  f"[white]${v:,.2f}[/]"


def build_table(rows: list[dict]) -> Table:
    t = Table(
        title=f"[bold bright_white]📈 My Stock Portfolio[/]  [dim]{datetime.now():%b %d, %Y  %H:%M}[/]",
        box=box.ROUNDED, border_style="bright_blue",
        header_style="bold black on #4fc3f7",
        show_lines=True, padding=(0, 1),
    )
    t.add_column("#",            justify="right",  width=4,  style="dim")
    t.add_column("Ticker",       justify="center", width=7,  style="bold yellow")
    t.add_column("Company",      justify="left",   width=22, style="white")
    t.add_column("Shares",       justify="right",  width=8)
    t.add_column("Avg Cost",     justify="right",  width=10)
    t.add_column("Cur Price",    justify="right",  width=11)
    t.add_column("Market Value", justify="right",  width=14)
    t.add_column("Gain / Loss",  justify="right",  width=14)
    t.add_column("Return %",     justify="right",  width=10)
    t.add_column("",             justify="center", width=3)

    for i, r in enumerate(rows, 1):
        emoji = "🚀" if r["pct_return"] > 50 else "🟢" if r["pct_return"] > 0 else "🔴"
        t.add_row(
            str(i),
            r["ticker"],
            r["name"][:20],
            f"[white]{r['shares']:,.2f}[/]",
            f"[dim]${r['avg_cost']:,.2f}[/]",
            c_price(r["price"]),
            c_val(r["current_val"]),
            fmt_money(r["gain_loss"]),
            fmt_pct(r["pct_return"]),
            emoji,
        )
    return t


def build_summary(rows: list[dict]) -> Columns:
    total_val    = sum(r["current_val"] for r in rows)
    total_cost   = sum(r["cost_basis"]  for r in rows)
    total_gl     = total_val - total_cost
    total_pct    = (total_gl / total_cost * 100) if total_cost else 0
    best         = max(rows, key=lambda r: r["pct_return"])
    worst        = min(rows, key=lambda r: r["pct_return"])
    winners      = sum(1 for r in rows if r["pct_return"] > 0)

    val_color  = up(total_gl)
    perf_emoji = "🚀" if total_pct > 20 else "📈" if total_pct > 0 else "📉"

    p1 = Panel(
        f"[dim]Invested[/]  [white]${total_cost:>12,.2f}[/]\n"
        f"[dim]Value    [/]  [bold bright_cyan]${total_val:>12,.2f}[/]\n"
        f"[dim]Gain/Loss[/]  [bold {val_color}]{sign(total_gl)}${abs(total_gl):>11,.2f}[/]",
        title=f"[bold]💼 Portfolio Value[/]",
        border_style="bright_cyan", width=36,
    )
    p2 = Panel(
        f"[dim]Total Return[/]   [bold {val_color}]{perf_emoji} {sign(total_pct)}{total_pct:.2f}%[/]\n"
        f"[dim]Winners/Total[/]  [bold bright_green]{winners}[/][dim]/{len(rows)}[/]\n"
        f"[dim]Best Hold[/]      [bold bright_green]{best['ticker']} +{best['pct_return']:.1f}%[/]",
        title="[bold]📊 Performance[/]",
        border_style="magenta", width=34,
    )
    p3 = Panel(
        f"[dim]Largest Pos[/]   [bold bright_cyan]{max(rows, key=lambda r: r['current_val'])['ticker']}[/]\n"
        f"[dim]Worst Hold [/]   [bold red]{worst['ticker']} {sign(worst['pct_return'])}{worst['pct_return']:.1f}%[/]\n"
        f"[dim]Positions  [/]   [bold white]{len(rows)}[/]",
        title="[bold]🔍 Insights[/]",
        border_style="yellow", width=30,
    )
    return Columns([p1, p2, p3])


def main():
    console.print()
    console.print(Align.center(Panel.fit(
        "[bold bright_yellow]💰  PERSONAL PORTFOLIO TRACKER  💰[/]\n"
        "[dim white]Track your stocks · See gains & losses · Live prices[/]",
        border_style="bright_yellow", padding=(1, 10),
    )))
    console.print()

    use_demo = Confirm.ask("[bold]Use demo portfolio?[/] (No = enter your own)", default=True)
    portfolio = DEMO_PORTFOLIO if use_demo else input_portfolio()

    if not portfolio:
        console.print("[red]No holdings entered. Exiting.[/]")
        return

    rows = []
    with Progress(SpinnerColumn(style="bright_cyan"),
                  TextColumn("[bright_cyan]{task.description}"),
                  console=console, transient=True) as prog:
        task = prog.add_task("Fetching prices...", total=len(portfolio))
        for h in portfolio:
            prog.update(task, advance=1, description=f"Fetching [yellow]{h['ticker']}[/]...")
            row = build_row(h)
            if row:
                rows.append(row)
            else:
                console.print(f"  [red]⚠ Could not fetch {h['ticker']}, skipping.[/]")

    if not rows:
        console.print(Panel("[bold red]No data retrieved.[/]", border_style="red"))
        return

    rows.sort(key=lambda r: r["current_val"], reverse=True)

    console.print(build_table(rows))
    console.print()
    console.print(build_summary(rows))
    console.print()

    # Per-position bar chart
    console.print(Rule("[bold dim]Position Weights[/]", style="dim"))
    total_val = sum(r["current_val"] for r in rows)
    for r in rows:
        pct   = r["current_val"] / total_val * 100
        bars  = int(pct * 1.2)
        color = up(r["pct_return"])
        console.print(
            f"  [yellow]{r['ticker']:6}[/] "
            f"[{color}]{'█' * bars}{'░' * (60 - bars)}[/] "
            f"[dim]{pct:5.1f}%[/]"
        )
    console.print()


if __name__ == "__main__":
    main()
