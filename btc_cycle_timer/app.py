import streamlit as st
from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import localize

st.set_page_config(page_title="BTC Cycle Timer", layout="wide")

lang = st.selectbox("🌐 Language", ["ua", "en", "fr"])
timers = get_all_timers()

st.title(localize("app.title", lang))
for key, val in timers.items():
    st.metric(localize(f"timer.{key}", lang), val)
