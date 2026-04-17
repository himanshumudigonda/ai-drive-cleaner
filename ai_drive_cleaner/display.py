from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
import os

console = Console()

def show_banner(model_name: str):
    """Display the application banner."""
    banner_text = f"[bold cyan]AI Drive Cleaner[/bold cyan]\nPowered by Groq AI\nActive Model: [green]{model_name}[/green]"
    console.print(Panel(banner_text, box=box.ROUNDED, expand=False))

def show_summary(total_files: int, total_size_str: str):
    """Show the pre-scan summary."""
    console.print(f"\n[bold]Scan Summary:[/bold]")
    console.print(f"Total files found: [yellow]{total_files}[/yellow]")
    console.print(f"Total size: [yellow]{total_size_str}[/yellow]\n")

def create_results_table() -> Table:
    """Create and return an empty Rich table for the results."""
    table = Table(box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Verdict", justify="center")
    table.add_column("Size", justify="right", style="cyan")
    table.add_column("Last Modified", style="magenta")
    table.add_column("File Path", style="dim", overflow="fold")
    table.add_column("AI Reason", style="italic")
    return table

def render_verdict(verdict: str) -> Text:
    if verdict == "SAFE_DELETE":
        return Text(verdict, style="bold red")
    elif verdict == "REVIEW":
        return Text(verdict, style="bold yellow")
    else:
        return Text(verdict, style="bold green")

def display_table(table: Table):
    console.print(table)

def show_total_reclaimable(size_str: str):
    console.print(f"\n[bold green]Total Reclaimable Space: {size_str}[/bold green]\n")
