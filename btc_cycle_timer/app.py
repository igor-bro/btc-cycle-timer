import streamlit as st
from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import localize
from btc_cycle_timer.chart import plot_cycle_phases

st.set_page_config(page_title="BTC Cycle Timer", layout="wide")

# 🌐 Вибір мови
lang = st.selectbox("🌐 Language", ["ua", "en", "fr"])

# 🕰️ Дані для таймерів
timers = get_all_timers()

# 🧾 Заголовок сторінки
st.title(localize("app.title", lang))

# 🕒 Вивід метрик таймерів
for key, val in timers.items():
    st.metric(localize(f"timer.{key}", lang), val)

# 📈 Графік фаз циклу
st.subheader(localize("chart.title", lang))
st.plotly_chart(plot_cycle_phases(lang=lang), use_container_width=True)

# ℹ️ Інформаційна секція
st.markdown("---")
st.markdown(localize("disclaimer", lang))
