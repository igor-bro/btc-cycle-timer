# status.py

from btc_cycle_timer.calc import calculate_cycle_stats

def get_progress_bar(length=30) -> tuple[str, float]:
    stats = calculate_cycle_stats()
    percent = stats["percent_progress"]
    filled_length = int(length * percent // 100)
    bar = "█" * filled_length + "░" * (length - filled_length)
    return bar, percent
