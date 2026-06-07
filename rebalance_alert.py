#!/usr/bin/env python3
"""
Portfolio Rebalancing Alert System
pip install yfinance rich matplotlib
"""

import yfinance as yf
import time
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich import box

console = Console()

# ── Portfolio ─────────────────────────────────────────────────────────────────
PORTFOLIO = [
    {"ticker": "NVDA", "shares": 10,  "entry_price": 205.00},
    {"ticker": "AAPL", "shares": 5,   "entry_price": 307.00},
    {"ticker": "AVGO", "shares": 10,  "entry_price": 385.00},
]

# ── Target Allocation by Sector (must sum to 100) ─────────────────────────────
TARGET_ALLOCATION = {
    "Semiconductors":       40.0,
    "Consumer Electronics": 30.0,
    "Infrastructure":       30.0,
}

DRIFT_THRESHOLD = 5.0  # % — flag if current deviates more than this from target

# ── Fallback data (network blocked in cloud) ──────────────────────────────────
FALLBACK_DATA = {
    "NVDA": {"sector": "Semiconductors",       "price": 1208.88, "name": "NVIDIA Corp"},
    "AAPL": {"sector": "Consumer Electronics", "price": 213.55,  "name": "Apple Inc"},
    "AVGO": {"sector": "Semiconductors",       "price": 1842.75, "name": "Broadcom Inc"},
}

SECTOR_COLORS = {
    "Semiconductors":       "#FF6B6B",
    "Consumer Electronics": "#4ECDC4",
    "Infrastructure":       "#45B7D1",
    "Unknown":              "#AAAAAA",
}


# ── Data Fetching ─────────────────────────────────────────────────────────────
def fetch_stock(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).info
        price = info.get("currentPrice") or info.get("lastPrice")
        sector = info.get("sector", "Unknown")
        name = info.get("shortName", ticker)
        if price and price > 0:
            return {"price": round(price, 2), "sector": sector, "name": name}
    except Exception:
        pass
    return FALLBACK_DATA.get(ticker, {"price": 0, "sector": "Unknown", "name": ticker})


# ── Calculations ──────────────────────────────────────────────────────────────
def calc_portfolio(portfolio):
    holdings = []
    for h in portfolio:
        data = fetch_stock(h["ticker"])
        current_val = h["shares"] * data["price"]
        cost_basis  = h["shares"] * h["entry_price"]
        holdings.append({
            **h,
            "name":        data["name"],
            "sector":      data["sector"],
            "price":       data["price"],
            "current_val": current_val,
            "cost_basis":  cost_basis,
            "gain_loss":   current_val - cost_basis,
            "gain_pct":    ((current_val - cost_basis) / cost_basis * 100) if cost_basis else 0,
        })
    return holdings


def calc_sector_allocation(holdings):
    sector_vals = defaultdict(float)
    total = sum(h["current_val"] for h in holdings)
    for h in holdings:
        sector_vals[h["sector"]] += h["current_val"]

    result = {}
    for sector, target in TARGET_ALLOCATION.items():
        current_val = sector_vals.get(sector, 0.0)
        current_pct = (current_val / total * 100) if total else 0
        drift       = current_pct - target
        result[sector] = {
            "current_pct": current_pct,
            "current_val": current_val,
            "target_pct":  target,
            "drift":       drift,
            "flagged":     abs(drift) > DRIFT_THRESHOLD,
        }

    # Flag unrecognised sectors (not in target)
    for sector, val in sector_vals.items():
        if sector not in TARGET_ALLOCATION:
            current_pct = (val / total * 100) if total else 0
            result[sector] = {
                "current_pct": current_pct,
                "current_val": val,
                "target_pct":  0.0,
                "drift":       current_pct,
                "flagged":     current_pct > DRIFT_THRESHOLD,
            }

    return result, total


# ── Display Tables ────────────────────────────────────────────────────────────
def holdings_table(holdings, total):
    t = Table(
        title=f"[bold bright_white]📋 Current Holdings[/]  [dim]{datetime.now():%b %d, %Y  %H:%M}[/]",
        box=box.ROUNDED, border_style="bright_blue",
        header_style="bold black on #4fc3f7",
        show_lines=True, padding=(0, 1),
    )
    t.add_column("Ticker",   justify="center", width=8,  style="bold yellow")
    t.add_column("Company",  justify="left",   width=18, style="white")
    t.add_column("Sector",   justify="left",   width=22, style="cyan")
    t.add_column("Shares",   justify="right",  width=8)
    t.add_column("Entry",    justify="right",  width=10)
    t.add_column("Price",    justify="right",  width=11)
    t.add_column("Value",    justify="right",  width=12)
    t.add_column("Wt %",     justify="right",  width=8)
    t.add_column("G/L",      justify="right",  width=14)

    for h in sorted(holdings, key=lambda x: x["current_val"], reverse=True):
        wt   = h["current_val"] / total * 100
        c    = "bright_green" if h["gain_loss"] >= 0 else "red"
        sign = "+" if h["gain_loss"] >= 0 else ""
        t.add_row(
            h["ticker"],
            h["name"][:16],
            h["sector"],
            f"{h['shares']:,.0f}",
            f"[dim]${h['entry_price']:,.2f}[/]",
            f"[white]${h['price']:,.2f}[/]",
            f"[bright_cyan]${h['current_val']:,.2f}[/]",
            f"[dim]{wt:.1f}%[/]",
            f"[bold {c}]{sign}${abs(h['gain_loss']):,.2f} ({sign}{h['gain_pct']:.1f}%)[/]",
        )
    return t


def rebalance_table(sector_data):
    t = Table(
        title="[bold bright_white]⚖️  Rebalancing Alert Dashboard[/]",
        box=box.DOUBLE_EDGE,
        border_style="bright_yellow",
        header_style="bold black on bright_yellow",
        show_lines=True, padding=(0, 1),
    )
    t.add_column("Sector",       justify="left",   width=22, style="cyan")
    t.add_column("Current %",    justify="right",  width=11)
    t.add_column("Target %",     justify="right",  width=10)
    t.add_column("Drift",        justify="right",  width=12)
    t.add_column("Current $",    justify="right",  width=12)
    t.add_column("Status",       justify="center", width=22)
    t.add_column("Action",       justify="left",   width=28)

    for sector, d in sorted(sector_data.items(),
                            key=lambda x: abs(x[1]["drift"]),
                            reverse=True):
        drift  = d["drift"]
        flagged = d["flagged"]

        drift_color = "bright_red" if flagged else ("green" if abs(drift) < 2 else "yellow")
        drift_sign  = "+" if drift >= 0 else ""

        if flagged:
            if drift > 0:
                status = "[bold bright_red]🚨 OVERWEIGHT[/]"
                action = f"[red]Trim by ~${abs(drift/100 * d['current_val'] / (d['current_pct']/100 if d['current_pct'] else 1)):,.0f}[/]"
            else:
                status = "[bold red]⚠️  UNDERWEIGHT[/]"
                needed = abs(drift) / 100 * sum(v["current_val"] for v in sector_data.values())
                action = f"[yellow]Add ~${needed:,.0f} to {sector}[/]"
        elif d["target_pct"] == 0:
            status = "[bold red]❌ NOT IN TARGET[/]"
            action = "[red]Consider rotating out[/]"
        elif abs(drift) <= 2:
            status = "[bold bright_green]✅ ON TARGET[/]"
            action = "[dim green]No action needed[/]"
        else:
            status = "[bold yellow]🟡 WATCH[/]"
            action = "[dim yellow]Monitor closely[/]"

        t.add_row(
            f"[bold]{sector}[/]",
            f"[bold white]{d['current_pct']:.1f}%[/]",
            f"[dim]{d['target_pct']:.1f}%[/]",
            f"[bold {drift_color}]{drift_sign}{drift:.1f}%[/]",
            f"[bright_cyan]${d['current_val']:,.2f}[/]",
            status,
            action,
        )
    return t


# ── Rebalancing Chart ─────────────────────────────────────────────────────────
def save_chart(sector_data, total):
    sectors = list(sector_data.keys())
    current = [sector_data[s]["current_pct"] for s in sectors]
    targets = [sector_data[s]["target_pct"] for s in sectors]
    drifts  = [sector_data[s]["drift"] for s in sectors]
    flagged = [sector_data[s]["flagged"] for s in sectors]

    x = np.arange(len(sectors))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), facecolor="#1a1a1a")
    fig.suptitle(
        f"Portfolio Rebalancing Dashboard  |  Total: ${total:,.2f}  |  {datetime.now():%b %d, %Y}",
        color="white", fontsize=13, weight="bold", y=1.01,
    )

    # ── Left: Grouped bar — current vs target ────────────────────────────────
    ax1.set_facecolor("#1a1a1a")
    bar_colors = [SECTOR_COLORS.get(s, "#AAAAAA") for s in sectors]
    flag_colors = ["#FF2222" if f else c for f, c in zip(flagged, bar_colors)]

    b1 = ax1.bar(x - width/2, current, width, label="Current %",
                 color=flag_colors, alpha=0.9, edgecolor="#1a1a1a", linewidth=1.5)
    b2 = ax1.bar(x + width/2, targets, width, label="Target %",
                 color="#FFFFFF", alpha=0.25, edgecolor="#FFFFFF", linewidth=1.5)

    # Value labels on bars
    for bar, val, flag in zip(b1, current, flagged):
        c = "#FF4444" if flag else "#ffffff"
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.1f}%", ha="center", va="bottom", color=c,
                 fontsize=9, weight="bold")
    for bar, val in zip(b2, targets):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.1f}%", ha="center", va="bottom", color="#aaaaaa",
                 fontsize=9)

    ax1.set_xticks(x)
    ax1.set_xticklabels(sectors, color="white", fontsize=9, rotation=10)
    ax1.set_ylabel("Allocation (%)", color="white")
    ax1.set_ylim(0, max(max(current), max(targets)) * 1.2)
    ax1.tick_params(colors="white")
    ax1.spines[:].set_color("#444444")
    ax1.set_title("Current vs Target Allocation", color="white", weight="bold", pad=12)
    ax1.legend(facecolor="#2a2a2a", labelcolor="white", edgecolor="#555555")
    ax1.axhline(y=DRIFT_THRESHOLD + max(targets), color="#FF4444",
                linestyle="--", alpha=0.3, linewidth=0.8)

    # Threshold band annotation
    for i, (t_pct, flag) in enumerate(zip(targets, flagged)):
        ax1.axhspan(t_pct - DRIFT_THRESHOLD, t_pct + DRIFT_THRESHOLD,
                    xmin=(i)/len(sectors) + 0.02,
                    xmax=(i+1)/len(sectors) - 0.02,
                    alpha=0.06, color="yellow")

    # ── Right: Drift bar chart ────────────────────────────────────────────────
    ax2.set_facecolor("#1a1a1a")
    drift_bar_colors = ["#FF3333" if f else ("#44DD44" if d >= 0 else "#FF8800")
                        for d, f in zip(drifts, flagged)]

    bars = ax2.bar(sectors, drifts, color=drift_bar_colors,
                   edgecolor="#1a1a1a", linewidth=1.5, alpha=0.9)

    # Threshold lines
    ax2.axhline(y= DRIFT_THRESHOLD, color="#FF4444", linestyle="--",
                linewidth=1.5, alpha=0.7, label=f"+{DRIFT_THRESHOLD}% threshold")
    ax2.axhline(y=-DRIFT_THRESHOLD, color="#FF4444", linestyle="--",
                linewidth=1.5, alpha=0.7, label=f"-{DRIFT_THRESHOLD}% threshold")
    ax2.axhline(y=0, color="#888888", linewidth=0.8)

    # Fill danger zones
    ymax = max(abs(min(drifts)), abs(max(drifts))) * 1.4 + DRIFT_THRESHOLD
    ax2.fill_between([-0.5, len(sectors) - 0.5],
                     DRIFT_THRESHOLD, ymax, alpha=0.07, color="red")
    ax2.fill_between([-0.5, len(sectors) - 0.5],
                     -ymax, -DRIFT_THRESHOLD, alpha=0.07, color="red")

    # Labels on bars
    for bar, val, flag in zip(bars, drifts, flagged):
        sign = "+" if val >= 0 else ""
        c = "#FF4444" if flag else "#ffffff"
        vert = "bottom" if val >= 0 else "top"
        offset = 0.3 if val >= 0 else -0.3
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + offset,
                 f"{sign}{val:.1f}%", ha="center", va=vert,
                 color=c, fontsize=10, weight="bold")

    ax2.set_xticklabels(sectors, color="white", fontsize=9, rotation=10)
    ax2.set_ylabel("Drift from Target (%)", color="white")
    ax2.set_ylim(-ymax, ymax)
    ax2.tick_params(colors="white")
    ax2.spines[:].set_color("#444444")
    ax2.set_title("Drift from Target  (🚨 = Action Required)", color="white",
                  weight="bold", pad=12)
    ax2.legend(facecolor="#2a2a2a", labelcolor="white", edgecolor="#555555", fontsize=9)

    # Flag alerts on overweight/underweight sectors
    for i, (s, flag, d) in enumerate(zip(sectors, flagged, drifts)):
        if flag:
            label = "SELL" if d > 0 else "BUY"
            ax2.text(i, d + (1.2 if d >= 0 else -1.2), f"🚨{label}",
                     ha="center", color="#FF4444", fontsize=9, weight="bold")

    plt.tight_layout()
    fname = "/home/user/claude-test/rebalance_dashboard.png"
    plt.savefig(fname, dpi=150, bbox_inches="tight", facecolor="#1a1a1a")
    return fname


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    start = time.time()

    console.print()
    console.print(Align.center(Panel.fit(
        "[bold bright_yellow]⚖️   PORTFOLIO REBALANCING ALERT SYSTEM   ⚖️[/]\n"
        "[dim]Drift threshold: ±5%  |  Compare current vs target allocation[/]",
        border_style="bright_yellow", padding=(1, 6),
    )))
    console.print()

    # Fetch & calculate
    console.print("[dim]Fetching prices...[/]\n")
    holdings = calc_portfolio(PORTFOLIO)
    sector_data, total = calc_sector_allocation(holdings)

    # Holdings table
    console.print(holdings_table(holdings, total))
    console.print()

    # Target allocation reminder
    tgt_str = "  ".join(
        f"[cyan]{s}[/]: [bold yellow]{p:.0f}%[/]"
        for s, p in TARGET_ALLOCATION.items()
    )
    console.print(Panel(tgt_str, title="[bold]🎯 Target Allocation[/]",
                        border_style="dim", padding=(0, 2)))
    console.print()

    # Rebalancing table
    console.print(rebalance_table(sector_data))
    console.print()

    # Summary panels
    flagged_sectors = [s for s, d in sector_data.items() if d["flagged"]]
    missing_sectors = [s for s in TARGET_ALLOCATION if s not in
                       {h["sector"] for h in holdings}]
    total_gain = sum(h["gain_loss"] for h in holdings)
    gain_color = "bright_green" if total_gain >= 0 else "red"
    sign = "+" if total_gain >= 0 else ""

    alert_text = (
        f"[bold bright_red]🚨 {len(flagged_sectors)} sector(s) need rebalancing:[/]\n"
        + "\n".join(f"  • [red]{s}[/]" for s in flagged_sectors)
        if flagged_sectors else
        "[bold bright_green]✅ Portfolio is within tolerance on all sectors[/]"
    )

    missing_text = (
        "[bold red]⚠️  Missing sectors:[/]\n"
        + "\n".join(f"  • [yellow]{s}[/] (target {TARGET_ALLOCATION[s]:.0f}%)" for s in missing_sectors)
        if missing_sectors else
        "[dim green]All target sectors represented[/]"
    )

    console.print(Columns([
        Panel(alert_text, title="[bold]🚨 Alerts[/]", border_style="bright_red", width=36),
        Panel(missing_text, title="[bold]📭 Missing Sectors[/]", border_style="yellow", width=34),
        Panel(
            f"[dim]Portfolio Value[/]  [bold bright_cyan]${total:>11,.2f}[/]\n"
            f"[dim]Total Gain/Loss[/]  [bold {gain_color}]{sign}${abs(total_gain):>11,.2f}[/]\n"
            f"[dim]Drift Threshold[/]  [bold white]±{DRIFT_THRESHOLD:.0f}%[/]",
            title="[bold]💼 Stats[/]", border_style="bright_cyan", width=32,
        ),
    ]))
    console.print()

    # Save chart
    console.print(Rule("[dim]Generating charts...[/]", style="dim"))
    fname = save_chart(sector_data, total)
    console.print(f"\n  [green]✓[/] Dashboard saved → [bold]{fname}[/]")

    elapsed = time.time() - start
    console.print(f"  [dim]⏱ Total execution time: {elapsed:.2f}s[/]\n")


if __name__ == "__main__":
    main()
