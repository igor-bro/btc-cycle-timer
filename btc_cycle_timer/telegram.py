import os
import requests
from dotenv import load_dotenv
from btc_cycle_timer.utils import localize
from btc_cycle_timer.logger import logger

load_dotenv()

def escape_md(text: str) -> str:
    """Escapes special characters for Markdown v2"""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return ''.join(f"\\{c}" if c in escape_chars else c for c in str(text))

def send_telegram_message(timers: dict, price: float, stats: dict, progress: float, lang: str):
    logger.info(f"Sending Telegram message (lang={lang})")
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # Localized headers
    title = escape_md(localize("app.title", lang))
    halving = escape_md(localize("timer.halving", lang))
    peak = escape_md(localize("timer.peak", lang))
    bottom = escape_md(localize("timer.bottom", lang))
    stat_title = escape_md(localize("telegram.stats", lang))
    current_price = escape_md(localize("price.current", lang))
    progress_title = escape_md(localize("progress.title", lang))
    unit_days = escape_md(localize("unit.days", lang))

    # Timers with emoji
    timer_text = (
        f"🟦 *{halving}*: `{timers['halving']}` {unit_days}\n"
        f"🟩 *{peak}*: `{timers['peak']}` {unit_days}\n"
        f"🟥 *{bottom}*: `{timers['bottom']}` {unit_days}"
    )

    # Statistics (ROI, days, prices)
    stat_lines = []
    for key, value in stats.items():
        label = escape_md(localize(f"stats.{key}", lang))
        if "roi" in key or "percent" in key:
            formatted = f"{value:.2f}\\%"
        elif "price" in key:
            formatted = f"${value:,.0f}".replace(",", "\\,")
        else:
            formatted = escape_md(str(value))
        stat_lines.append(f"• *{label}*: `{formatted}`")
    stats_block = "\n".join(stat_lines)

    # Complete message
    text = (
        f"*📅 {title}*\n\n"
        f"{timer_text}\n\n"
        f"💰 *{current_price}*: `${price:,.2f}`\n"
        f" *{progress_title}*: `{progress:.2f}\\%`\n\n"
        f"*📊 {stat_title}:*\n"
        f"{stats_block}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2"
    }

    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Telegram error: {response.text}")
    logger.info("Telegram message sent successfully")

# Export functions
__all__ = ['send_telegram_message', 'escape_md']
