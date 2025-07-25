import json
from pathlib import Path
from rich.table import Table
from rich.console import Console


def localize(key: str, lang: str = "en") -> str:
    """Повертає перекладене значення ключа з JSON-файлу локалізації."""
    path = Path(__file__).parent / f"lang/{lang}.json"
    if not path.exists():
        return key
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, key)
    except Exception:
        return key


def render_cli(timers: dict, lang: str):
    """Виводить таблицю з таймерами у CLI з локалізацією."""
    console = Console()
    table = Table(title=localize("app.title", lang))

    table.add_column(localize("table.label", lang))
    table.add_column(localize("table.value", lang))

    for key, val in timers.items():
        table.add_row(localize(f"timer.{key}", lang), f"{val:,}")

    console.print(table)
