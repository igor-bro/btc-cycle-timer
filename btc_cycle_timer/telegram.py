import os
import requests
from dotenv import load_dotenv
from btc_cycle_timer.utils import localize

load_dotenv()

def send_telegram_message(timers: dict, price: float, stats: dict, progress: float, lang: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    title = localize("app.title", lang)
    halving = localize("timer.halving", lang)
    peak = localize("timer.peak", lang)
    bottom = localize("timer.bottom", lang)
    stat_title = localize("telegram.stats", lang)

    # Форматування секції таймерів
    timer_text = (
        f"{halving}: {timers['halving']} {localize('unit.days', lang)}\n"
        f"{peak}: {timers['peak']} {localize('unit.days', lang)}\n"
        f"{bottom}: {timers['bottom']} {localize('unit.days', lang)}"
    )

    # Форматування секції статистики
    stat_lines = []
    for key, value in stats.items():
        label = localize(f"stats.{key}", lang)
        if "roi" in key or "percent" in key:
            formatted = f"{value:.2f}%"
        elif "price" in key:
            formatted = f"${value:,.0f}"
        else:
            formatted = str(value)
        stat_lines.append(f"▪️ {label}: {formatted}")
    stats_block = "\n".join(stat_lines)

    # Повне повідомлення
    text = (
        f"*📅 {title}*\n\n"
        f"{timer_text}\n\n"
        f"💰 {localize('price.current', lang)}: ${price:,.2f}\n"
        f"📉 {localize('progress.title', lang)}: {progress:.2f}%\n\n"
        f"*📊 {stat_title}:*\n"
        f"{stats_block}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Telegram error: {response.text}")
