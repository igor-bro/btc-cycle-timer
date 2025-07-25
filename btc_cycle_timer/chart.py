import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from btc_cycle_timer.utils import localize

def generate_cycle_phases(start_date: datetime = datetime(2022, 11, 22)):
    phases = [
        ("Accumulation", 0, 180, "#6c757d"),
        ("Parabolic", 180, 730, "#28a745"),
        ("Distribution", 730, 1000, "#ffc107"),
        ("Capitulation", 1000, 1460, "#dc3545"),
    ]

    data = []
    for name, start_offset, end_offset, color in phases:
        phase_start = start_date + timedelta(days=start_offset)
        phase_end = start_date + timedelta(days=end_offset)
        data.append({
            "Phase": name,
            "Start": phase_start,
            "End": phase_end,
            "Color": color
        })

    return pd.DataFrame(data)

def plot_cycle_phases(lang="en"):
    df = generate_cycle_phases()
    fig = px.timeline(
        df, x_start="Start", x_end="End", y="Phase", color="Phase",
        color_discrete_map={row["Phase"]: row["Color"] for _, row in df.iterrows()},
        title=localize("chart.title", lang)
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title=localize("chart.x_axis", lang),
        yaxis_title=localize("chart.y_axis", lang),
        legend_title=localize("chart.legend", lang)
    )
    return fig
