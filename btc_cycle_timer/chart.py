# chart.py

import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from glob import glob

from .utils import localize
from .timer import get_forecast_dates
from .config import (
    CYCLE_BOTTOM_DATE, FORECAST_PEAK_PRICE, FORECAST_BOTTOM_PRICE,
    PHASE_ACCUMULATION_START, PHASE_ACCUMULATION_END,
    PHASE_PARABOLIC_START, PHASE_PARABOLIC_END,
    PHASE_DISTRIBUTION_START, PHASE_DISTRIBUTION_END,
    PHASE_CAPITULATION_START, PHASE_CAPITULATION_END,
    PREVIOUS_CYCLE_PEAK
)
from .calc import get_current_btc_price

def load_price_data(data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), "data")
    all_files = sorted(glob(os.path.join(data_dir, "btc_price_*.csv")))
    dfs = []

    for f in all_files:
        df = pd.read_csv(f)
        if "date" in df.columns and "close" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df[["date", "close"]]
            dfs.append(df)

    if not dfs:
        raise ValueError("No valid price data files found.")

    return pd.concat(dfs).sort_values("date")

def get_price_on(date: datetime, df: pd.DataFrame) -> float:
    nearest = df[df["date"] <= date]
    if not nearest.empty:
        return float(nearest.iloc[-1]["close"])
    return None

def plot_cycle_phases(lang="en", show_projection=False):
    df_price = load_price_data()

    today = datetime.now()
    max_date = today + timedelta(days=180)

    df_price = df_price[(df_price["date"] >= CYCLE_BOTTOM_DATE) & (df_price["date"] <= max_date)]
    forecast = get_forecast_dates()
    filtered_forecast = {k: v for k, v in forecast.items() if v <= max_date}

    phases = [
        (localize("phase.accumulation", lang), PHASE_ACCUMULATION_START, PHASE_ACCUMULATION_END, "#6c757d"),
        (localize("phase.parabolic", lang), PHASE_PARABOLIC_START, PHASE_PARABOLIC_END, "#28a745"),
        (localize("phase.distribution", lang), PHASE_DISTRIBUTION_START, PHASE_DISTRIBUTION_END, "#ffc107"),
        (localize("phase.capitulation", lang), PHASE_CAPITULATION_START, PHASE_CAPITULATION_END, "#dc3545"),
    ]

    filtered_phases = []
    for name, start_offset, end_offset, color in phases:
        x0 = CYCLE_BOTTOM_DATE + timedelta(days=start_offset)
        x1 = CYCLE_BOTTOM_DATE + timedelta(days=end_offset)
        if x0 > max_date:
            continue
        x1 = min(x1, max_date)
        filtered_phases.append((name, x0, x1, color))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_price["date"], y=df_price["close"],
        mode="lines", name=localize("line.btc_price", lang), line=dict(color="white", width=2)
    ))

    max_price = max(220_000, df_price["close"].max() * 1.2)

    for name, x0, x1, color in filtered_phases:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=max_price,
                      fillcolor=color, opacity=0.2, line=dict(width=0), layer="below")
        fig.add_trace(go.Scatter(
            x=[x0 + (x1 - x0) / 2],
            y=[max_price * 0.95],
            text=[name],
            mode="text",
            showlegend=False
        ))

    event_labels = {
        "bottom": localize("event.bottom", lang),
        "halving_prev": localize("event.halving", lang),
        "halving": localize("event.halving", lang),
        "peak": localize("event.peak", lang),
        "bottom_forecast": localize("event.bottom_forecast", lang)
    }

    for key, label in event_labels.items():
        date = forecast.get("bottom" if key == "bottom_forecast" else key)
        if not date or date < df_price["date"].min() or date > max_date:
            continue
        fig.add_vline(x=date, line_width=1, line_dash="dash", line_color="deepskyblue")
        fig.add_annotation(
            x=date,
            y=max_price * 1.02,
            text=label,
            showarrow=False,
            font=dict(color="deepskyblue", size=12),
            bgcolor="black",
            opacity=0.7
        )

    bottom_price_val = get_price_on(CYCLE_BOTTOM_DATE, df_price)
    if bottom_price_val:
        fig.add_trace(go.Scatter(
            x=[CYCLE_BOTTOM_DATE, max_date],
            y=[bottom_price_val, bottom_price_val],
            mode="lines",
            line=dict(color="gray", dash="dot"),
            name=localize("line.prev_bottom", lang)
        ))

    if forecast["peak"] <= max_date:
        fig.add_shape(
            type="rect",
            x0=forecast["peak"],
            x1=min(forecast["peak"] + timedelta(days=180), max_date),
            y0=FORECAST_PEAK_PRICE - 20000,
            y1=FORECAST_PEAK_PRICE,
            fillcolor="red",
            opacity=0.25,
            layer="below",
            line=dict(width=0)
        )

    if forecast["bottom"] <= max_date:
        fig.add_shape(
            type="rect",
            x0=forecast["bottom"],
            x1=min(forecast["bottom"] + timedelta(days=180), max_date),
            y0=FORECAST_BOTTOM_PRICE,
            y1=FORECAST_BOTTOM_PRICE + 20000,
            fillcolor="green",
            opacity=0.25,
            layer="below",
            line=dict(width=0)
        )

    next_event_key = None
    min_days_diff = float("inf")
    for key in ["peak", "bottom"]:
        event_date = forecast.get(key)
        if event_date and event_date >= today:
            days_diff = (event_date - today).days
            if days_diff < min_days_diff:
                min_days_diff = days_diff
                next_event_key = key

    if next_event_key:
        event_date = forecast[next_event_key]
        days_text = f"{min_days_diff} {localize('unit.days', lang)}"
        mid_date = today + (event_date - today) / 2
        mid_price = get_price_on(today, df_price)

        if mid_price:
            fig.add_annotation(
                x=mid_date,
                y=mid_price * 0.85,  # Переміщуємо нижче
                text=f"⏳ {days_text} → ",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-30,  # Стрілка вниз
                font=dict(color="orange", size=10),
                bgcolor="black",
                opacity=0.8
            )

    if show_projection:
        # Pass full data for pattern projection
        full_df = load_price_data()
        plot_pattern_projection(fig, full_df, lang=lang)

    fig.update_layout(
        title=localize("chart.title", lang),
        title_x=0.1,
        xaxis_title=localize("chart.x_axis", lang),
        yaxis_title="BTC Price (USD)",
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color="white"),
        height=680,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=13)),
        yaxis=dict(tick0=0, dtick=20000, showgrid=True, gridcolor="#222"),
        xaxis=dict(tickformat="%b\n%Y\n", dtick="M1", showgrid=True, gridcolor="#222", nticks=12, tickangle=45)
    )

    return fig

def plot_pattern_projection(fig, df, lang="en"):
    try:
        forecast = get_forecast_dates()
        forecast_peak = forecast.get("peak")
        if not forecast_peak:
            return

        today = datetime.now()
        days_to_peak = (forecast_peak - today).days
        
        if days_to_peak <= 0:
            return

        # Find previous cycle peak
        previous_peak_date = PREVIOUS_CYCLE_PEAK
        
        # Take period N days BEFORE peak + N days AFTER peak (where N = days to current peak)
        start_pattern_date = previous_peak_date - timedelta(days=days_to_peak)
        end_pattern_date = previous_peak_date + timedelta(days=days_to_peak)
        
        # Filter data for pattern
        pattern_df = df[(df["date"] >= start_pattern_date) & (df["date"] <= end_pattern_date)].copy()
        if pattern_df.empty:
            return

        # Calculate date projection
        pattern_df["days"] = (pattern_df["date"] - pattern_df["date"].min()).dt.days
        pattern_df["projected_date"] = today + pd.to_timedelta(pattern_df["days"], unit="D")

        # Scale prices
        current_price = get_price_on(today, df)
        if current_price is None:
            return
            
        first_pattern_price = pattern_df["close"].iloc[0]
        if first_pattern_price <= 0:
            return
            
        scale = current_price / first_pattern_price
        pattern_df["adjusted_close"] = pattern_df["close"] * scale

        # Add projection line
        trace_name = localize("line.pattern_projection", lang)
        
        fig.add_trace(go.Scatter(
            x=pattern_df["projected_date"],
            y=pattern_df["adjusted_close"],
            mode="lines",
            name=trace_name,
            line=dict(color="cyan", dash="dot", width=2),
            opacity=0.8
        ))

    except Exception as e:
        # Silent error handling for production
        pass

# Експорт функцій
__all__ = ['plot_cycle_phases', 'plot_pattern_projection', 'load_price_data', 'get_price_on']
