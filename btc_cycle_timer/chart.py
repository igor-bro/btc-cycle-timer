# chart.py

import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from glob import glob
from .utils import localize
from .timer import get_forecast_dates


def load_price_data(data_dir="btc_cycle_timer/data/"):
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


def plot_cycle_phases(lang="en"):
    df_price = load_price_data()

    today = datetime.today()
    max_date = today + timedelta(days=180)

    # Фільтруємо ціну
    df_price = df_price[df_price["date"] <= max_date]

    # Початок графіку — з останнього дна
    start_date = datetime(2022, 11, 22) 
    df_price = df_price[df_price["date"] >= start_date]

    # Прогнозовані дати
    forecast = get_forecast_dates()

    # Фільтруємо всі майбутні події
    filtered_forecast = {k: v for k, v in forecast.items() if v <= max_date}

    # Фази циклу (залишаємо тільки ті, що не виходять за межі max_date)
    phases = [
        ("Accumulation", 0, 180, "#6c757d"),
        ("Parabolic", 180, 730, "#28a745"),
        ("Distribution", 730, 1000, "#ffc107"),
        ("Capitulation", 1000, 1460, "#dc3545"),
    ]
    filtered_phases = []
    for name, start_offset, end_offset, color in phases:
        x0 = start_date + timedelta(days=start_offset)
        x1 = start_date + timedelta(days=end_offset)
        if x0 > max_date:
            continue
        x1 = min(x1, max_date)
        filtered_phases.append((name, x0, x1, color))

    fig = go.Figure()

    # Лінія ціни BTC
    fig.add_trace(go.Scatter(
        x=df_price["date"], y=df_price["close"],
        mode="lines", name="BTC Price", line=dict(color="white", width=2)
    ))

    # Фонові зони фаз
    max_price = max(220_000, df_price["close"].max() * 1.2)
    for name, x0, x1, color in filtered_phases:
        fig.add_shape(
            type="rect",
            x0=x0, x1=x1,
            y0=0, y1=max_price,
            fillcolor=color,
            opacity=0.2,
            line=dict(width=0),
            layer="below"
        )
        fig.add_trace(go.Scatter(
            x=[x0 + (x1 - x0) / 2],
            y=[max_price * 0.95],
            text=[name],
            mode="text",
            showlegend=False
        ))

    # Вертикальні лінії подій (тільки якщо дата <= max_date)
    event_labels = {
        "bottom": "📉 Bottom",
        "halving_prev": "📆 Halving",
        "halving": "📆 Halving",
        "peak": "🚀 Forecasted Peak",
        "bottom_forecast": "📉 Forecasted Bottom"
    }

    event_dates = []
    for key, label in event_labels.items():
        if key == "bottom_forecast":
            if "bottom" in forecast:
                event_dates.append((label, forecast["bottom"]))
        elif key in forecast:
            event_dates.append((label, forecast[key]))

    for label, date in event_dates:
        if date < df_price["date"].min() or date > max_date:
            continue
        fig.add_vline(
            x=date,
            line_width=1 if "Halving" in label or "Peak" in label or "Bottom" in label else 2,
            line_dash="dash",
            line_color="deepskyblue"
        )
        fig.add_annotation(
            x=date,
            y=max_price * 1.02,
            text=label,
            showarrow=False,
            font=dict(color="deepskyblue", size=12),
            bgcolor="black",
            opacity=0.7
        )
    
    # Горизонтальна лінія на рівні ціни минулого дна
    price_bottom = df_price[df_price["date"] == start_date]["close"]
    if price_bottom.empty:
    
        # Якщо точної дати немає, беремо найближчу меншу
        price_bottom = df_price[df_price["date"] <= start_date]["close"]
    if not price_bottom.empty:
        price_bottom_val = float(price_bottom.iloc[-1])
        fig.add_trace(go.Scatter(
            x=[start_date, max_date],
            y=[price_bottom_val, price_bottom_val],
            mode="lines",
            line=dict(color="gray", dash="dot"),
            name="Previous Bottom Level"
        ))

    # Горизонтальні лінії (тільки якщо обидві дати <= max_date)
    if forecast["peak"] <= max_date:
        fig.add_trace(go.Scatter(
            x=[forecast["peak"], min(forecast["peak"] + timedelta(days=180), max_date)],
            y=[200000, 200000],
            mode="lines",
            line=dict(color="tomato", dash="dash", width=1),
            name="Forecasted Peak Level"
        ))

    if forecast["bottom"] <= max_date:
        fig.add_trace(go.Scatter(
            x=[forecast["bottom"], min(forecast["bottom"] + timedelta(days=480), max_date)],
            y=[get_price_on(forecast["bottom"]), get_price_on(forecast["bottom"])],
            mode="lines",
            line=dict(color="gray", dash="dot"),
            name="Bottom Level"
        ))
        fig.add_trace(go.Scatter(
            x=[forecast["bottom"], min(forecast["bottom"] + timedelta(days=60), max_date)],
            y=[get_price_on(forecast["bottom"]), get_price_on(forecast["bottom"])],
            mode="lines",
            line=dict(color="gray", dash="dot"),
            name="Forecasted Bottom Level"
        ))

    # Стиль
    fig.update_layout(
        title=localize("chart.title", lang),
        title_x=0.1,    
        xaxis_title=localize("chart.x_axis", lang),
        yaxis_title="BTC Price (USD)",
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color="white"),
        height=680,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=13)
        ),
        yaxis=dict(
            tick0=0,
            dtick=20000,
            showgrid=True,
            gridcolor="#222"
        ),
        xaxis=dict(
            tickformat="%b\n%Y\n",
            dtick="M1",
            showgrid=True,
            gridcolor="#222",
            nticks=12,
            tickangle=45 
        )
    )

    return fig