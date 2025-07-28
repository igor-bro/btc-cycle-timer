# BTC Cycle Timer API Documentation

## Overview

BTC Cycle Timer is a Python package that provides tools for analyzing Bitcoin's 4-year market cycles, including timers, price analysis, and pattern projection.

## Installation

```bash
pip install btc-cycle-timer
```

## Core Functions

### Timer Functions

#### `get_all_timers()`

Returns countdown timers for key Bitcoin cycle events.

**Returns:**

```python
{
    'halving': int,    # Days until next halving
    'peak': int,       # Days until forecasted peak
    'bottom': int      # Days until forecasted bottom
}
```

**Example:**

```python
from btc_cycle_timer import get_all_timers

timers = get_all_timers()
print(f"Days to halving: {timers['halving']}")
```

#### `get_forecast_dates()`

Returns forecasted dates for cycle events.

**Returns:**

```python
{
    'halving': datetime,      # Next halving date
    'peak': datetime,         # Forecasted peak date
    'bottom': datetime,       # Forecasted bottom date
    'halving_prev': datetime  # Previous halving date
}
```

### Price Functions

#### `get_btc_price()`

Fetches current Bitcoin price from Binance API with CSV fallback.

**Returns:**

```python
float  # Current BTC price in USD, or None if unavailable
```

**Example:**

```python
from btc_cycle_timer import get_btc_price

price = get_btc_price()
if price:
    print(f"Current BTC price: ${price:,.2f}")
```

### Analysis Functions

#### `calculate_cycle_stats()`

Calculates cycle statistics and ROI projections.

**Returns:**

```python
{
    'days_from_bottom': int,
    'percent_progress': float,
    'roi_from_bottom': float,
    'roi_to_peak': float,
    'roi_bottom_to_peak': float,
    'forecast_peak_price': float,
    'forecast_bottom_price': float
}
```

#### `get_progress_bar()`

Returns progress bar data for current cycle.

**Returns:**

```python
(str, float)  # (progress bar string, percentage complete)
```

### Chart Functions

#### `plot_cycle_phases(lang="en", show_projection=False)`

Creates a Plotly chart showing Bitcoin cycle phases.

**Parameters:**

- `lang` (str): Language code ('en', 'ua', 'fr')
- `show_projection` (bool): Whether to show pattern projection

**Returns:**

```python
plotly.graph_objects.Figure  # Interactive chart
```

**Example:**

```python
from btc_cycle_timer import plot_cycle_phases

fig = plot_cycle_phases(lang="en", show_projection=True)
fig.show()
```

### Localization

#### `localize(key, lang)`

Translates text keys to specified language.

**Parameters:**

- `key` (str): Translation key
- `lang` (str): Language code

**Returns:**

```python
str  # Translated text
```

**Example:**

```python
from btc_cycle_timer import localize

title = localize("app.title", "ua")
print(title)  # "Таймер 4-річного циклу Біткоїна"
```

## CLI Interface

### Command Line Usage

```bash
# Basic usage
btc-cycle

# With language specification
btc-cycle --lang=ua

# Direct Python execution
python -m btc_cycle_timer --lang=en
```

### CLI Options

- `--lang`: Language selection (en, ua, fr)
- `--help`: Show help message

## Web Interface

### Streamlit App

```bash
streamlit run btc_cycle_timer/app.py
```

**Features:**

- Interactive charts with pattern projection
- Real-time timer updates
- Multilingual interface
- Cycle statistics display

## Configuration

### Environment Variables

```bash
# Telegram Bot (optional)
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# App Settings
APP_LANGUAGE=ua
DEBUG=false
```

### Configuration Constants

Key constants are defined in `btc_cycle_timer.config`:

```python
from btc_cycle_timer.config import (
    LAST_HALVING,      # 2024-04-20
    NEXT_HALVING,      # 2028-04-20
    CYCLE_PEAK,        # 2025-10-11
    CYCLE_BOTTOM,      # 2026-10-30
    FORECAST_PEAK_PRICE,    # 200000
    FORECAST_BOTTOM_PRICE   # 75000
)
```

## Data Sources

### Price Data

- **Primary**: Binance API (real-time)
- **Fallback**: Local CSV files (2020-2025)
- **Format**: Daily OHLCV data

### Historical Data Files

```
btc_cycle_timer/data/
├── btc_price_2020.csv
├── btc_price_2021.csv
├── btc_price_2022.csv
├── btc_price_2023.csv
├── btc_price_2024.csv
└── btc_price_2025.csv
```

## Error Handling

The package implements graceful error handling:

- **API Failures**: Falls back to CSV data
- **Missing Data**: Returns None with logging
- **Invalid Inputs**: Validates and provides defaults

## Performance

### Benchmarks

- **Data Loading**: < 1 second
- **Chart Rendering**: < 5 seconds
- **Memory Usage**: < 100MB
- **Pattern Projection**: < 2 seconds

## Examples

### Complete Usage Example

```python
from btc_cycle_timer import (
    get_all_timers, get_btc_price, calculate_cycle_stats,
    plot_cycle_phases, localize
)

# Get current status
timers = get_all_timers()
price = get_btc_price()
stats = calculate_cycle_stats()

# Display information
print(f"Days to halving: {timers['halving']}")
print(f"Current price: ${price:,.2f}")
print(f"Cycle progress: {stats['percent_progress']:.1f}%")

# Create chart
fig = plot_cycle_phases(lang="en", show_projection=True)
fig.show()
```

### Telegram Integration

```python
from btc_cycle_timer import send_telegram_message

# Send status update
send_telegram_message(lang="ua")
```

## Version History

- **v0.1.1**: Pattern projection, code cleanup, performance optimization
- **v0.1.0**: Initial release with basic functionality

## Support

For issues and questions:

- GitHub: https://github.com/igor-bro/btc-cycle-timer
- Email: kushneruk.igor@gmail.com
