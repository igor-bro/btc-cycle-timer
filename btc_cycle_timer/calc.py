# btc_cycle_timer/calc.py

from datetime import datetime
import requests

# Фіксовані дати дна і піку для поточного циклу (можеш змінити)
CYCLE_BOTTOM_DATE = datetime(2022, 11, 22)
CYCLE_PEAK_DATE = datetime(2025, 10, 15)
CYCLE_PEAK_PRICE = 200000  # Прогнозований пік

def get_current_btc_price() -> float:
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        return response.json()["bitcoin"]["usd"]
    except Exception:
        return None

def calculate_cycle_stats():
    today = datetime.utcnow()
    current_price = get_current_btc_price()
    bottom_price = 15700  # Ціна BTC на 22 листопада 2022

    days_from_bottom = (today - CYCLE_BOTTOM_DATE).days
    total_cycle_days = (CYCLE_PEAK_DATE - CYCLE_BOTTOM_DATE).days
    percent_progress = round(days_from_bottom / total_cycle_days * 100, 2)

    roi_from_bottom = round((current_price - bottom_price) / bottom_price * 100, 2)
    roi_to_peak = round((CYCLE_PEAK_PRICE - current_price) / current_price * 100, 2)
    roi_bottom_to_peak = round((CYCLE_PEAK_PRICE - bottom_price) / bottom_price * 100, 2)

    return {
        "days_from_bottom": days_from_bottom,
        "percent_progress": percent_progress,
        "roi_from_bottom": roi_from_bottom,
        "roi_to_peak": roi_to_peak,
        "roi_bottom_to_peak": roi_bottom_to_peak,
        "current_price": current_price
    }
