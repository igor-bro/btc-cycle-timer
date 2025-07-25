import streamlit as st
from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import localize
from btc_cycle_timer.chart import plot_cycle_phases
from btc_cycle_timer.calc import calculate_cycle_stats
from btc_cycle_timer.status import get_progress_bar
from datetime import timedelta

st.set_page_config(page_title="BTC Cycle Timer", layout="wide")

# 🌐 Вибір мови
lang = st.selectbox("🌐 Language", ["ua", "en", "fr"])

# 🕰️ Дані для таймерів
timers = get_all_timers()

# 🧾 Заголовок сторінки
st.title(localize("app.title", lang))


# 🕒 Вивід трьох таймерів у рядок
cols = st.columns(3)

for i, key in enumerate(["halving", "peak", "bottom"]):
    days = timers[key]
    hours = int((timers[key] - int(timers[key])) * 24)
    label = localize(f"timer.{key}", lang)

    # Форматування словоформ
    def pluralize(n, forms):
        if lang == "ua":
            return (
                forms[0] if n % 10 == 1 and n % 100 != 11 else
                forms[1] if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14) else
                forms[2]
            )
        else:
            return forms[1] if n != 1 else forms[0]

    day_word = pluralize(int(days), ["день", "дні", "днів"])
    hour_word = pluralize(hours, ["година", "години", "годин"])

    with cols[i]:
        st.subheader(f"{label}")
        st.markdown(f"**{int(days)} {day_word} {hours} {hour_word}**")

# 📈 Графік фаз циклу
st.subheader(localize("chart.title", lang))
st.plotly_chart(plot_cycle_phases(lang=lang), use_container_width=True)

bar, percent = get_progress_bar()
st.subheader(localize("progress.title", lang))
st.progress(int(percent))
st.caption(localize("progress.caption", lang).format(percent=percent))

stats = calculate_cycle_stats()
st.subheader(localize("progress.stats", lang))
st.json(stats)


# ℹ️ Інформаційна секція
st.markdown("---")
st.markdown(localize("disclaimer", lang))
