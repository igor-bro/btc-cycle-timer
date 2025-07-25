from datetime import datetime
import requests

# Історичні дати
CYCLE_BOTTOM_DATE = datetime(2022, 11, 22)
CYCLE_PEAK_DATE = datetime(2025, 10, 15)

# Історичні ціни
BOTTOM_PRICE = 15700
PEAK_PRICE = None  # ще не відомо

# Прогнозовані ціни
FORECAST_PEAK_PRICE = 200000
FORECAST_BOTTOM_PRICE = 75000


def get_current_btc_price() -> float:
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return float(response.json()["price"])
    except Exception as e:
        print(f"⚠️ Binance API error: {e}")
        return None 

def calculate_cycle_stats():
    today = datetime.utcnow()
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
    total_cycle_days = (CYCLE_PEAK_DATE - CYCLE_BOTTOM_DATE).days
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
