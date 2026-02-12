#!/usr/bin/env python3
"""
HARDCARD SWARM VISUALIZER
=========================
Live CLI dashboard for monitoring the Hardcard World Economy.
Displays Agent GDP, Treasury Reserves, and active Settlement Escrows.
"""

import time
import random
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from hardcard.treasury import genesis_treasury
from hardcard.market import SettlementEngine

console = Console()

def make_dashboard_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    return layout

def generate_treasury_panel() -> Panel:
    metrics = genesis_treasury.get_metrics()
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_row("[bold cyan]Treasury ID[/]", metrics["id"])
    table.add_row("[bold cyan]Agent GDP[/]", f"[bold green]{metrics['agent_gdp_reserve']} $HCL[/]")
    table.add_row("[bold cyan]Transactions[/]", str(metrics["transaction_count"]))
    table.add_row("[bold cyan]Protocol[/]", "HPSS-02 (Shielded)")
    table.add_row("[bold cyan]Network[/]", "WORLD")
    
    return Panel(
        table,
        title="[bold white]🏛️ CENTRAL TREASURY[/]",
        border_style="cyan"
    )

def generate_agent_swarm_panel() -> Panel:
    # Simulated agent activity
    table = Table(box=box.SIMPLE)
    table.add_column("Agent ID", style="magenta")
    table.add_column("Activity", style="white")
    table.add_column("Contribution", style="green")
    
    agents = [
        ("AIVA_VET_01", "Assessed Feline Pain", "4.50"),
        ("BOT_RX_99", "Refilled Medication", "1.20"),
        ("DOLITTLE_02", "Optical Flow Respiration", "15.00"),
        ("SENTINEL_X", "Repaired UI Regression", "8.00"),
        ("MUNDI_00", "Updated Geo-Risk Heatmap", "2.00"),
    ]
    
    for agent, activity, contribution in agents:
        table.add_row(agent, activity, f"+{contribution} $HCL")
        
    return Panel(
        table,
        title="[bold white]🐝 AGENT SWARM ACTIVITY[/]",
        border_style="magenta"
    )

def generate_escrow_panel() -> Panel:
    table = Table(box=box.SIMPLE)
    table.add_column("Escrow ID", style="yellow")
    table.add_column("Worker", style="white")
    table.add_column("TTL Left", style="cyan")
    table.add_column("Status", style="bold")
    
    # Mock some active escrows
    escrows = [
        ("HCL-681", "vet_agent", "14m 20s", "[yellow]PENDING[/]"),
        ("HCL-992", "code_agent", "01h 05m", "[green]VERIFIED[/]"),
        ("HCL-334", "legal_agent", "23h 59m", "[yellow]PENDING[/]"),
    ]
    
    for eid, worker, ttl, status in escrows:
        table.add_row(eid, worker, ttl, status)
        
    return Panel(
        table,
        title="[bold white]🛡️ ACTIVE SETTLEMENTS[/]",
        border_style="yellow"
    )

class Header:
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(
            "[bold white]HARDCARD SOVEREIGN VISUALIZER[/] | "
            f"[bold cyan]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/] | "
            "[bold green]NETWORK: CANON_SETTLED[/]"
        )
        return Panel(grid, style="bold cyan on black")

class Footer:
    def __rich__(self) -> Panel:
        return Panel(
            "[bold white]ESC: Quit[/] | [bold white]R: Refresh[/] | [bold white]T: Snapshot[/]",
            style="bold white on black",
            box=box.SIMPLE
        )

def main():
    layout = make_dashboard_layout()
    header = Header()
    footer = Footer()
    
    with Live(layout, refresh_per_second=2, screen=True):
        while True:
            # Update data
            layout["header"].update(header)
            layout["left"].update(generate_treasury_panel())
            layout["right"].split(
                Layout(generate_agent_swarm_panel(), ratio=1),
                Layout(generate_escrow_panel(), ratio=1)
            )
            layout["footer"].update(footer)
            
            # Simulate real-time logic
            if random.random() > 0.8:
                # Mock a small GDP growth
                genesis_treasury.agent_gdp_reserve += 0.05
                genesis_treasury.transaction_count += 1
            
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
