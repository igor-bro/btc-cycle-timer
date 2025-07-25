from datetime import date
from btc_cycle_timer.config import NEXT_HALVING, CYCLE_PEAK, CYCLE_BOTTOM
from datetime import datetime, timedelta

def get_timer_dates():
    reference_date = datetime.today()
    timers = get_all_timers()
    return {
        "halving": (reference_date + timedelta(days=int(timers["halving"]))).strftime("%d.%m.%Y"),
        "peak": (reference_date + timedelta(days=int(timers["peak"]))).strftime("%d.%m.%Y"),
        "bottom": (reference_date + timedelta(days=int(timers["bottom"]))).strftime("%d.%m.%Y")
    }

def get_forecast_dates():
    """
    Повертає прогнозовані дати подій циклу:
    - пік (peak)
    - дно (bottom)
    - халвінг (halving)
    """
    base_dates = {
        "halving": datetime(2028, 4, 20),
        "peak": datetime(2025, 10, 11),
        "bottom": datetime(2026, 10, 30),
    }
    now = datetime.utcnow()
    return {
        key: now + timedelta(days=delta.total_seconds() / 86400)
        if (delta := (date - now)).total_seconds() > 0 else date
        for key, date in base_dates.items()
    }


def days_until(target: date) -> int:
    return (target - date.today()).days

def get_all_timers() -> dict:
    return {
        "halving": days_until(NEXT_HALVING),
        "peak": days_until(CYCLE_PEAK),
        "bottom": days_until(CYCLE_BOTTOM),
    }
