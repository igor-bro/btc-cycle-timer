import streamlit as st
from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import localize as base_localize
from btc_cycle_timer.chart import plot_cycle_phases
from btc_cycle_timer.calc import calculate_cycle_stats
from btc_cycle_timer.status import get_progress_bar
from datetime import datetime, timedelta

# --- Custom CSS for better visuals, responsiveness, and animation ---
st.markdown("""
    <style>
        h1, h2, h4, h5 { text-align: center; }
        .stProgress > div > div > div > div {
            background-color: #1E90FF;
        }
        .timer-block {
            border-radius: 12px;
            background: transparent;
            box-shadow: none;
            padding: 1.2em 0.5em 1em 0.5em;
            margin-bottom: 1em;
            animation: fadeIn 1.2s;
        }
        .disclaimer {
            font-size: 0.95em;
            color: #888;
            text-align: center;
        }
        .top-bar {
            position: relative;
            width: 100%;
            margin-bottom: 1.5em;
        }
        .lang-select { text-align: left; }
        .refresh-btn {
            position: absolute;
            top: 0;
            right: 0;
            z-index: 100;
            text-align: right;
        }
        .refresh-btn button {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }
        .timer-block h5 {
            font-size: 1.1em;
            margin-bottom: 0.3em;
        }
        @media (max-width: 900px) {
            .timer-block { font-size: 0.95em; }
            .top-bar { flex-direction: column; gap: 0.5em; }
            .lang-select, .refresh-btn { text-align: center; position: static; }
        }
        @media (max-width: 600px) {
            .timer-block { font-size: 0.9em; }
            h1 { font-size: 2em; }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: none; }
        }
        .block-spacer { margin: 2em 0 1.5em 0; }
        .stat-metric {
            border-radius: 10px;
            padding: 0.7em 0.5em;
            margin-bottom: 0.7em;
            margin-top: 0.7em;
        }
        .stat-blue { background: #eaf4ff; color: #1E90FF; }
        .stat-green { background: #eafbe7; color: #28a745; }
        .stat-red { background: #ffeaea; color: #e74c3c; }
        .stat-neutral { background: #23272f; color: #fff; }
        .stat-metric .stMetricLabel, .stat-metric .stMetricValue { font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- Custom CSS for stat cards and info icon ---
st.markdown("""
    <style>
        .stat-card {
            background: #181c23;
            border-radius: 14px;
            box-shadow: 0 2px 8px rgba(30,144,255,0.07);
            padding: 1.2em 1em 1em 1em;
            margin-bottom: 1.2em;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: box-shadow 0.2s, transform 0.2s;
        }
        .stat-card:hover {
            box-shadow: 0 4px 16px rgba(30,144,255,0.15);
            transform: translateY(-2px) scale(1.03);
        }
        .stat-label {
            font-size: 1em;
            color: #b0b8c9;
            margin-bottom: 0.3em;
            display: flex;
            align-items: center;
            gap: 0.2em;
            text-align: center;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #fff;
            font-family: monospace;
            text-align: center;
        }
        .stat-icon {
            font-size: 1.2em;
            margin-right: 0.2em;
        }
        .stat-info {
            display: inline-block;
            position: relative;
            font-size: 1.1em;
            color: #b0b8c9;
            margin-left: 0.2em;
            cursor: pointer;
            vertical-align: middle;
        }
        .stat-info:hover .stat-tooltip-box {
            display: block;
        }
        .stat-tooltip-box {
            display: none;
            position: absolute;
            left: 50%;
            top: 0;
            transform: translateX(-50%) translateY(-100%);
            background: #23272f;
            color: #fff;
            border-radius: 8px;
            padding: 0.7em 1em;
            font-size: 0.95em;
            min-width: 180px;
            z-index: 9999;
            box-shadow: 0 2px 8px rgba(30,144,255,0.10);
            white-space: pre-line;
        }
        .stat-blue { background: #d0e7ff; color: #1E90FF; }
        .stat-green { background: #d6f5e7; color: #28a745; }
        .stat-red { background: #ffe3e3; color: #e74c3c; }
        .stat-neutral { background: #23272f; color: #fff; }
        .stat-gold { background: #fff7e0; color: #e6b800; }
        .stat-mint { background: #e0fff7; color: #00b894; }
        .stat-purple { background: #d6d0ff; color: #7c3aed; }
        @media (max-width: 900px) {
            .stat-card { min-height: 100px; }
        }
        @media (max-width: 700px) {
            .stat-card { min-width: 90vw; margin-left: auto; margin-right: auto; }
        }
        @media (max-width: 600px) {
            .stat-card { min-width: 98vw; margin-left: auto; margin-right: auto; }
        }
    </style>
""", unsafe_allow_html=True)

# --- Custom CSS for top bar alignment ---
st.markdown("""
    <style>
    .topbar-flex {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 2em;
        gap: 1.5em;
    }
    .topbar-flex .stButton > button {
        margin-bottom: 0.1em;
    }
    </style>
""", unsafe_allow_html=True)

# --- Improved localize with fallback and formatting ---
def localize(key, lang, **kwargs):
    val = base_localize(key, lang)
    if val == key and lang != "en":
        val = base_localize(key, "en")
    try:
        return val.format(**kwargs)
    except Exception:
        return val

# --- Language selector with URL query support ---
lang_options = {
    "🇺🇦 Українська": "ua",
    "🇬🇧 English": "en",
    "🇫🇷 Français": "fr",
}

# Отримати мову з query_params (якщо є)
query_params = st.query_params 
initial_lang = query_params.get("lang", [st.session_state.get("lang", "en")])[0]

# Визначити початкову мову для selectbox
initial_index = list(lang_options.values()).index(initial_lang)
selected_label = st.selectbox(
    label="",
    options=list(lang_options.keys()),
    index=initial_index,
    label_visibility="collapsed"
)

# Оновити мову
lang = lang_options[selected_label]
st.session_state["lang"] = lang


# --- Data ---
timers = get_all_timers()
stats = calculate_cycle_stats()

# --- Title ---
st.markdown(f"<h1>{localize('app.title', lang)}</h1>", unsafe_allow_html=True)

# --- Timers block ---
st.markdown("<div class='block-spacer'></div>", unsafe_allow_html=True)
timer_cols = st.columns(3)
colors = {"halving": "#1E90FF", "peak": "#28a745", "bottom": "#e74c3c"}
timer_tooltips = {
    "halving": localize("timer.halving", lang) + ": " + localize("unit.days", lang) + ". " + localize("timer.halving.tooltip", lang, default="Countdown to the next scheduled halving event."),
    "peak": localize("timer.peak", lang) + ": " + localize("unit.days", lang) + ". " + localize("timer.peak.tooltip", lang, default="Forecasted days until the next cycle peak based on historical data."),
    "bottom": localize("timer.bottom", lang) + ": " + localize("unit.days", lang) + ". " + localize("timer.bottom.tooltip", lang, default="Forecasted days until the next cycle bottom based on historical data.")
}
for i, key in enumerate(["halving", "peak", "bottom"]):
    days = int(timers[key])
    date_key = f"timer.{key}_date"
    label = localize(f"timer.{key}", lang)
    date_val = localize(date_key, lang)
    with timer_cols[i]:
        st.markdown(f"<div class='timer-block' style='background: transparent; box-shadow: none;'>" \
            f"<h5 style='color: {colors[key]}; font-size: 1em;' title='{timer_tooltips[key]}'>{label}</h5>" \
            f"<h2 style='color: {colors[key]};'>{days} {localize('unit.days', lang)}</h2>" \
            + (f"<p style='color: {colors[key]}; font-size: 12px;'>({date_val})</p>" if date_val != date_key and date_val.strip() else "") \
            + "</div>", unsafe_allow_html=True)

# --- Progress Bar ---
st.markdown("<div class='block-spacer'></div>", unsafe_allow_html=True)
st.markdown(f"<h4> {localize('progress.title', lang)}</h4>", unsafe_allow_html=True)
bar, percent = get_progress_bar()
progress_bar_html = f"""
<div style='width: 100%; max-width: 600px; margin: 0 auto; background: #222; border-radius: 12px; height: 28px; box-shadow: 0 2px 8px rgba(30,144,255,0.10);'>
  <div style='width: {percent}%; background: linear-gradient(90deg, #1E90FF 60%, #28a745 100%); height: 100%; border-radius: 12px; transition: width 1s cubic-bezier(.4,2,.6,1);'></div>
</div>
<p style='text-align: center; margin-top: 8px; font-size: 1rem; color: #fff;'>{localize('progress.caption', lang, percent=f"{percent:.2f}")}</p>
"""
st.markdown(progress_bar_html, unsafe_allow_html=True)

# --- Chart of cycle phases ---
st.markdown("""
    <style>
    .full-width-chart .element-container {
        width: 100vw !important;
        max-width: 100vw !important;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("<div class='block-spacer'></div>", unsafe_allow_html=True)
st.markdown('<div class="full-width-chart">', unsafe_allow_html=True)
st.plotly_chart(plot_cycle_phases(lang=lang), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Cycle stats ---
st.markdown("<div class='block-spacer'></div>", unsafe_allow_html=True)
st.markdown(f"<h4 style='margin-top: 2em;'>{localize('telegram.stats', lang)}</h4>", unsafe_allow_html=True)
stat_cols = st.columns(3)
stat_blocks = [
    [
        ("stats.roi_from_bottom", f"{stats['roi_from_bottom']:.2f} %", "stat-blue", "#1E90FF", "📈", "ROI from the last bottom to now, based on price data."),
        ("stats.roi_to_peak", f"{stats['roi_to_peak']:.2f} %", "stat-green", "#28a745", "🚀", "ROI from now to the forecasted peak."),
        ("stats.roi_bottom_to_peak", f"{stats['roi_bottom_to_peak']:.2f} %", "stat-purple", "#7c3aed", "🟣", "ROI from the last bottom to the forecasted peak.")
    ],
    [
        ("stats.days_from_bottom", stats["days_from_bottom"], "stat-neutral", "#fff", "⏳", "Number of days since the last cycle bottom."),
        ("stats.percent_progress", f"{stats['percent_progress']:.2f} %", "stat-neutral", "#fff", "📊", "Percent of the cycle completed from bottom to peak.")
    ],
    [
        ("stats.forecast_peak_price", f"${stats['forecast_peak_price']:,}", "stat-gold", "#e6b800", "💰", "Forecasted price at the next cycle peak."),
        ("stats.forecast_bottom_price", f"${stats['forecast_bottom_price']:,}", "stat-mint", "#00b894", "💸", "Forecasted price at the next cycle bottom.")
    ]
]
for col, blocks in zip(stat_cols, stat_blocks):
    with col:
        for key, value, card_class, value_color, icon, default_help in blocks:
            label = localize(key, lang)
            help_text = base_localize(f"{key}.tooltip", lang)
            if help_text == f"{key}.tooltip":
                help_text = default_help
            st.markdown(f"""
                <div class="stat-card {card_class}">
                    <div class="stat-label">
                        <span class="stat-icon">{icon}</span>{label}
                        <span class="stat-info">ⓘ
                            <span class="stat-tooltip-box">{help_text}</span>
                        </span>
                    </div>
                    <div class="stat-value" style="color:{value_color};">{value}</div>
                </div>
            """, unsafe_allow_html=True)

# --- Disclaimer ---
st.markdown("<div class='block-spacer'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(f"<div class='disclaimer'>{localize('disclaimer', lang)}</div>", unsafe_allow_html=True)

st.markdown("---")
# --- Analogy text (footer.analogy) ---
st.markdown(f"<div class='disclaimer' style='margin-top: 2em;'>{localize('footer.analogy', lang)}</div>", unsafe_allow_html=True)
