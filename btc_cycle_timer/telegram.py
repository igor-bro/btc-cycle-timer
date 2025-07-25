import os
import requests
from dotenv import load_dotenv
from btc_cycle_timer.utils import localize

load_dotenv()

def send_telegram_message(data: dict, price: float, lang: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    title = localize("app.title", lang)
    halving = localize("timer.halving", lang)
    peak = localize("timer.peak", lang)
    bottom = localize("timer.bottom", lang)

    text = f"📈 *{title}*\n\n" \
           f"{halving}: {data['halving']} днів\n" \
           f"{peak}: {data['peak']} днів\n" \
           f"{bottom}: {data['bottom']} днів\n\n" \
           f"💰 BTC: ${price}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Telegram error: {response.text}")
