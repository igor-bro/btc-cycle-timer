from datetime import date
from btc_cycle_timer.config import NEXT_HALVING, CYCLE_PEAK, CYCLE_BOTTOM

def days_until(target: date) -> int:
    return (target - date.today()).days

def get_all_timers() -> dict:
    return {
        "halving": days_until(NEXT_HALVING),
        "peak": days_until(CYCLE_PEAK),
        "bottom": days_until(CYCLE_BOTTOM),
    }
