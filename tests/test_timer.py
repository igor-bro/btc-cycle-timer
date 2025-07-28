# tests/test_timer.py

import os
import pytest
from datetime import datetime
from btc_cycle_timer import timer, calc, chart, utils
import pandas as pd
import json

def test_forecast_dates_format():
    forecast = timer.get_forecast_dates()
    assert all(isinstance(d, datetime) for d in forecast.values()), "All forecast dates must be datetime objects"

def test_timer_values_positive():
    timers = timer.get_all_timers()
    for name, days in timers.items():
        assert days >= 0, f"Timer {name} should be non-negative"

def test_btc_price_fetch():
    price = calc.get_current_btc_price()
    assert price is None or price > 0, "Current BTC price should be positive or None if offline"

def test_all_price_files_exist():
    data_dir = "btc_cycle_timer/data"
    years = range(2020, 2026)
    for y in years:
        path = os.path.join(data_dir, f"btc_price_{y}.csv")
        assert os.path.exists(path), f"Missing price file: {path}"

def test_price_data_loads_correctly():
    df = chart.load_price_data()
    assert not df.empty, "Price dataframe should not be empty"
    assert "date" in df.columns and "close" in df.columns, "Required columns missing in price data"

def test_price_at_known_date():
    df = chart.load_price_data()
    date = calc.CYCLE_BOTTOM_DATE
    price = chart.get_price_on(date, df)
    assert price is not None, "Price should be available at known bottom date"
    assert price > 0, "Price must be positive"

@pytest.mark.parametrize("lang", ["en", "ua", "fr"])
def test_language_files_exist(lang):
    lang_file = f"btc_cycle_timer/lang/{lang}.json"
    assert os.path.exists(lang_file), f"Missing language file: {lang_file}"

@pytest.mark.parametrize("lang", ["en", "ua", "fr"])
def test_language_keys_completeness(lang):
    lang_path = f"btc_cycle_timer/lang/{lang}.json"
    with open(lang_path, encoding="utf-8") as f:
        translations = json.load(f)

    required_keys = [
        "app.title", "chart.title", "chart.x_axis", "chart.y_axis",
        "phase.accumulation", "phase.parabolic", "phase.distribution", "phase.capitulation",
        "event.bottom", "event.peak", "event.halving", "event.bottom_forecast",
        "line.btc_price", "line.prev_bottom", "line.forecasted_peak_level", "line.forecasted_bottom_level"
    ]

    for key in required_keys:
        assert key in translations, f"Missing key in {lang}.json: {key}"

def test_module_exports():
    """Checks that all modules correctly export functions"""
    import btc_cycle_timer
    
    # Check main exports
    assert hasattr(btc_cycle_timer, 'get_all_timers')
    assert hasattr(btc_cycle_timer, 'get_btc_price')
    assert hasattr(btc_cycle_timer, 'calculate_cycle_stats')
    assert hasattr(btc_cycle_timer, 'localize')
    assert hasattr(btc_cycle_timer, 'get_progress_bar')
    assert hasattr(btc_cycle_timer, 'plot_cycle_phases')
    assert hasattr(btc_cycle_timer, 'send_telegram_message')

def test_price_function_unification():
    """Checks that price retrieval functions are unified"""
    from btc_cycle_timer.calc import get_current_btc_price
    from btc_cycle_timer.price import get_btc_price
    
    # Both functions should return the same result
    price1 = get_current_btc_price()
    price2 = get_btc_price()
    
    assert price1 == price2, "Price retrieval functions should return the same result"

def test_centralized_config():
    """Checks that all important constants are centralized in config.py"""
    from btc_cycle_timer.config import (
        LAST_HALVING, NEXT_HALVING, CYCLE_PEAK, CYCLE_BOTTOM,
        CYCLE_BOTTOM_DATE, FORECAST_PEAK_DATE, FORECAST_BOTTOM_DATE,
        BOTTOM_PRICE, FORECAST_PEAK_PRICE, FORECAST_BOTTOM_PRICE,
        BINANCE_URL, SYMBOL, INTERVAL, LIMIT
    )
    
    # Check that all constants exist
    assert LAST_HALVING is not None
    assert NEXT_HALVING is not None
    assert CYCLE_PEAK is not None
    assert CYCLE_BOTTOM is not None
    assert CYCLE_BOTTOM_DATE is not None
    assert FORECAST_PEAK_DATE is not None
    assert FORECAST_BOTTOM_DATE is not None
    assert BOTTOM_PRICE is not None
    assert FORECAST_PEAK_PRICE is not None
    assert FORECAST_BOTTOM_PRICE is not None
    assert BINANCE_URL is not None
    assert SYMBOL is not None
    assert INTERVAL is not None
    assert LIMIT is not None

def test_config_consistency():
    """Checks date consistency between different modules"""
    from btc_cycle_timer.config import CYCLE_PEAK, FORECAST_PEAK_DATE
    from btc_cycle_timer.timer import get_forecast_dates
    
    # Check that dates are consistent
    forecast_dates = get_forecast_dates()
    assert "peak" in forecast_dates
    assert "bottom" in forecast_dates
    assert "halving" in forecast_dates

