# timer.py

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
    from .config import LAST_HALVING, NEXT_HALVING, FORECAST_PEAK_DATE, FORECAST_BOTTOM_DATE
    
    base_dates = {
        "halving_prev": datetime.combine(LAST_HALVING, datetime.min.time()),
        "halving": datetime.combine(NEXT_HALVING, datetime.min.time()),
        "peak": FORECAST_PEAK_DATE,
        "bottom": FORECAST_BOTTOM_DATE,
    }
    now = datetime.now()
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

# Експорт функцій
__all__ = ['get_all_timers', 'get_timer_dates', 'get_forecast_dates', 'days_until']
