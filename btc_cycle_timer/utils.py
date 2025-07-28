import json
from pathlib import Path
from rich.table import Table
from rich.console import Console
from btc_cycle_timer.status import get_progress_bar
from btc_cycle_timer.calc import calculate_cycle_stats
from btc_cycle_timer.config import NEXT_HALVING, CYCLE_PEAK, CYCLE_BOTTOM
from btc_cycle_timer.logger import logger


def localize(key: str, lang: str = "en", **kwargs) -> str:
    logger.debug(f"Localizing key: {key} for lang: {lang}")
    path = Path(__file__).parent / f"lang/{lang}.json"
    if not path.exists():
        return key
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, key)
    except Exception:
        return key


def render_cli(timers: dict, price: float, lang: str):
    logger.info("Rendering CLI output")
    console = Console()
    
    # Dates for table
    dates = {
        "halving": NEXT_HALVING.strftime("%Y-%m-%d"),
        "peak": CYCLE_PEAK.strftime("%Y-%m-%d"),
        "bottom": CYCLE_BOTTOM.strftime("%Y-%m-%d")
    }

    # Timers
    table = Table(title=f"📅 {localize('app.title', lang)}")
    table.add_column(localize("table.label", lang))
    table.add_column(localize("table.value", lang))

    for key, val in timers.items():
        label = localize(f"timer.{key}", lang)
        date_str = dates.get(key, "")
        table.add_row(label, f"{val} {localize('unit.days', lang)} ({date_str})")

    console.print(table)

    # Progress
    bar, percent = get_progress_bar()
    console.print(f"\n[bold magenta]{localize('progress.title', lang)}: {percent:.2f}%[/bold magenta]")
    console.print(f"[green]{bar}[/green]")

    # Statistics
    console.print(f"\n📊 {localize('telegram.stats', lang)}:")
    stats = calculate_cycle_stats()

    for key, value in stats.items():
        label = localize(f"stats.{key}", lang)
        if "roi" in key or "percent" in key:
            formatted = f"{value:.2f}%"
        elif "price" in key:
            formatted = f"${value:,.0f}"
        else:
            formatted = str(round(value, 2))
        console.print(f"▪️ {label}: [cyan]{formatted}[/cyan]")

# Export functions
__all__ = ['localize', 'render_cli']
