import json
from pathlib import Path

def localize(key: str, lang: str = "ua") -> str:
    path = Path(__file__).parent / "lang" / f"{lang}.json"
    if not path.exists():
        return key
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get(key, key)

def render_cli(timers: dict, lang="ua"):
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="BTC Cycle Timer")

    table.add_column("Подія")
    table.add_column("Днів до")

    for key, val in timers.items():
        table.add_row(localize(f"timer.{key}", lang), str(val))
    
    console.print(table)
