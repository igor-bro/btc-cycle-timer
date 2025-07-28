# timer.py

from datetime import date
from btc_cycle_timer.config import NEXT_HALVING, CYCLE_PEAK, CYCLE_BOTTOM
from datetime import datetime, timedelta
from btc_cycle_timer.logger import logger

def get_timer_dates():
    logger.debug("Calculating timer dates...")
    reference_date = datetime.today()
    timers = get_all_timers()
    return {
        "halving": (reference_date + timedelta(days=int(timers["halving"]))).strftime("%d.%m.%Y"),
        "peak": (reference_date + timedelta(days=int(timers["peak"]))).strftime("%d.%m.%Y"),
        "bottom": (reference_date + timedelta(days=int(timers["bottom"]))).strftime("%d.%m.%Y")
    }

def get_forecast_dates():
    logger.debug("Getting forecast dates for cycle events...")
    """
    Returns forecasted dates for cycle events:
    - peak
    - bottom
    - halving
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
    logger.debug(f"Calculating days until {target}")
    return (target - date.today()).days

def get_all_timers() -> dict:
    logger.info("Getting all timers for cycle events")
    return {
        "halving": days_until(NEXT_HALVING),
        "peak": days_until(CYCLE_PEAK),
        "bottom": days_until(CYCLE_BOTTOM),
    }

# Export functions
__all__ = ['get_all_timers', 'get_timer_dates', 'get_forecast_dates', 'days_until']
