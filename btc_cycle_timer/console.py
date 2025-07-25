#console.py

from rich.console import Console
from rich.table import Table
from rich.columns import Columns

console = Console()
success = lambda msg: console.print(f"[bold green]✔ {msg}[/bold green]")
info = lambda msg: console.print(f"[bold cyan]ℹ {msg}[/bold cyan]")
error = lambda msg: console.print(f"[bold red]✘ {msg}[/bold red]")

__all__ = ["console", "success", "info", "error", "Table", "Columns"]
