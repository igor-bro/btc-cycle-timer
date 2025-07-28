# config.py

from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple
import json
import os
from pathlib import Path

# === CYCLE CONFIGURATION ===
CYCLE_LENGTH_DAYS = 1460  # ~4 years
HALVING_INTERVAL_DAYS = 1460  # ~4 years

# === CURRENT CYCLE DATES ===
# Halvings
LAST_HALVING = date(2024, 4, 20)
NEXT_HALVING = date(2028, 4, 20)

# Current cycle forecast
CYCLE_PEAK = date(2025, 10, 11)
CYCLE_BOTTOM = date(2026, 10, 30)

# === HISTORICAL DATES ===
# Previous cycle data
PREVIOUS_CYCLE_PEAK = datetime(2021, 11, 10)
CYCLE_BOTTOM_DATE = datetime(2022, 11, 22)

# === FORECASTED DATES (datetime) ===
FORECAST_PEAK_DATE = datetime(2025, 10, 15)
FORECAST_BOTTOM_DATE = datetime(2026, 10, 30)

# === PRICES ===
# Historical prices
BOTTOM_PRICE = 15700
PEAK_PRICE = None  # Will be updated when current cycle peak is reached

# Forecasted prices
FORECAST_PEAK_PRICE = 200000
FORECAST_BOTTOM_PRICE = 75000

# === API SETTINGS ===
BINANCE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1d"
LIMIT = 366

# === CYCLE PHASES (days from bottom) ===
PHASE_ACCUMULATION_START = 0
PHASE_ACCUMULATION_END = 180
PHASE_PARABOLIC_START = 180
PHASE_PARABOLIC_END = 730
PHASE_DISTRIBUTION_START = 730
PHASE_DISTRIBUTION_END = 1000
PHASE_CAPITULATION_START = 1000
PHASE_CAPITULATION_END = 1460

# === DYNAMIC CYCLE MANAGEMENT ===
CYCLE_HISTORY_FILE = "cycle_history.json"

def get_cycle_history() -> List[Dict]:
    """Load cycle history from file"""
    history_file = Path(__file__).parent / CYCLE_HISTORY_FILE
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_cycle_history(history: List[Dict]):
    """Save cycle history to file"""
    history_file = Path(__file__).parent / CYCLE_HISTORY_FILE
    try:
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving cycle history: {e}")

def calculate_next_cycle_dates(current_peak_date: date, current_bottom_date: date) -> Tuple[date, date]:
    """Calculate next cycle dates based on current cycle"""
    cycle_length = (current_peak_date - current_bottom_date).days
    
    # Estimate next cycle based on historical patterns
    next_peak_date = current_peak_date + timedelta(days=CYCLE_LENGTH_DAYS)
    next_bottom_date = current_bottom_date + timedelta(days=CYCLE_LENGTH_DAYS)
    
    return next_peak_date, next_bottom_date

def get_current_cycle_phase() -> str:
    """Determine current cycle phase"""
    today = date.today()
    days_since_bottom = (today - CYCLE_BOTTOM_DATE.date()).days
    
    if days_since_bottom <= PHASE_ACCUMULATION_END:
        return "accumulation"
    elif days_since_bottom <= PHASE_PARABOLIC_END:
        return "parabolic"
    elif days_since_bottom <= PHASE_DISTRIBUTION_END:
        return "distribution"
    elif days_since_bottom <= PHASE_CAPITULATION_END:
        return "capitulation"
    else:
        return "unknown"

def should_update_cycle_config() -> bool:
    """Check if cycle configuration needs updating"""
    today = date.today()
    
    # Update if we're past the forecasted peak date
    if today > CYCLE_PEAK:
        return True
    
    # Update if we're past the forecasted bottom date
    if today > CYCLE_BOTTOM:
        return True
    
    return False

def get_future_cycles(count: int = 3) -> List[Dict]:
    """Get forecasted dates for future cycles"""
    cycles = []
    current_peak = CYCLE_PEAK
    current_bottom = CYCLE_BOTTOM
    
    for i in range(count):
        next_peak, next_bottom = calculate_next_cycle_dates(current_peak, current_bottom)
        
        cycles.append({
            "cycle_number": i + 1,
            "peak_date": next_peak,
            "bottom_date": next_bottom,
            "halving_date": NEXT_HALVING + timedelta(days=i * HALVING_INTERVAL_DAYS)
        })
        
        current_peak = next_peak
        current_bottom = next_bottom
    
    return cycles

# === CYCLE VALIDATION ===
def validate_cycle_config() -> List[str]:
    """Validate cycle configuration and return any issues"""
    issues = []
    
    # Check date consistency
    if CYCLE_PEAK <= CYCLE_BOTTOM_DATE.date():
        issues.append("Cycle peak should be after historical bottom")
    
    if CYCLE_BOTTOM <= CYCLE_PEAK:
        issues.append("Cycle bottom should be after cycle peak")
    
    # Check price consistency
    if FORECAST_PEAK_PRICE <= FORECAST_BOTTOM_PRICE:
        issues.append("Forecast peak price should be higher than bottom price")
    
    return issues

# Export constants and functions
__all__ = [
    'LAST_HALVING', 'NEXT_HALVING', 'CYCLE_PEAK', 'CYCLE_BOTTOM',
    'PREVIOUS_CYCLE_PEAK', 'CYCLE_BOTTOM_DATE', 'FORECAST_PEAK_DATE', 'FORECAST_BOTTOM_DATE',
    'BOTTOM_PRICE', 'PEAK_PRICE', 'FORECAST_PEAK_PRICE', 'FORECAST_BOTTOM_PRICE',
    'BINANCE_URL', 'SYMBOL', 'INTERVAL', 'LIMIT',
    'PHASE_ACCUMULATION_START', 'PHASE_ACCUMULATION_END',
    'PHASE_PARABOLIC_START', 'PHASE_PARABOLIC_END',
    'PHASE_DISTRIBUTION_START', 'PHASE_DISTRIBUTION_END',
    'PHASE_CAPITULATION_START', 'PHASE_CAPITULATION_END',
    'get_cycle_history', 'save_cycle_history', 'calculate_next_cycle_dates',
    'get_current_cycle_phase', 'should_update_cycle_config', 'get_future_cycles',
    'validate_cycle_config'
]
