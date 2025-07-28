#calc.py

from datetime import datetime
from .price import get_btc_price
from .config import (
    CYCLE_BOTTOM_DATE, FORECAST_PEAK_DATE, BOTTOM_PRICE, PEAK_PRICE,
    FORECAST_PEAK_PRICE, FORECAST_BOTTOM_PRICE
)
from btc_cycle_timer.logger import logger

# Export functions
__all__ = ['get_current_btc_price', 'calculate_cycle_stats']


def get_current_btc_price() -> float:
    """Alias for get_btc_price from price module"""
    logger.info("Getting current BTC price (alias)")
    return get_btc_price() 

def calculate_cycle_stats():
    logger.info("Calculating cycle statistics...")
    today = datetime.now()
    current_price = get_current_btc_price()
    if current_price is None:
        return {
            "days_from_bottom": 0,
            "percent_progress": 0,
            "roi_from_bottom": 0,
            "roi_to_peak": 0,
            "roi_bottom_to_peak": 0,
            "current_price": 0
        }


    days_from_bottom = (today - CYCLE_BOTTOM_DATE).days
    total_cycle_days = (FORECAST_PEAK_DATE - CYCLE_BOTTOM_DATE).days
    percent_progress = round(days_from_bottom / total_cycle_days * 100, 2)

    roi_from_bottom = round((current_price - BOTTOM_PRICE) / BOTTOM_PRICE * 100, 2)
    roi_to_peak = round((FORECAST_PEAK_PRICE - current_price) / current_price * 100, 2)
    roi_bottom_to_peak = round((FORECAST_PEAK_PRICE - BOTTOM_PRICE) / BOTTOM_PRICE * 100, 2)

    return {
        "days_from_bottom": days_from_bottom,
        "percent_progress": percent_progress,
        "roi_from_bottom": roi_from_bottom,
        "roi_to_peak": roi_to_peak,
        "roi_bottom_to_peak": roi_bottom_to_peak,
        "forecast_peak_price": FORECAST_PEAK_PRICE,
        "forecast_bottom_price": FORECAST_BOTTOM_PRICE,
    }
