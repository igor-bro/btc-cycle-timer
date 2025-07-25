# entry point for CLI

from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import render_cli
from btc_cycle_timer.price import get_btc_price
from btc_cycle_timer.telegram import send_telegram_message
import argparse

def main():
    parser = argparse.ArgumentParser(description="BTC Cycle CLI")
    parser.add_argument("--lang", default="ua", choices=["ua", "en", "fr"])
    args = parser.parse_args()
    
    data = get_all_timers()
    render_cli(data, lang=args.lang)

    price = get_btc_price()
    print(f"\nCurrent BTC Price: ${price}")
    
    
    if input("Send to Telegram? (y/n): ").lower() == "y":
        send_telegram_message(data, price, lang=args.lang)
