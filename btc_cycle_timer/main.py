# entry point for CLI

import argparse
from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import render_cli, localize
from btc_cycle_timer.price import get_btc_price
from btc_cycle_timer.telegram import send_telegram_message
from btc_cycle_timer.calc import calculate_cycle_stats
from btc_cycle_timer.status import get_progress_bar

def main():
    parser = argparse.ArgumentParser(description="BTC Cycle CLI")
    parser.add_argument("--lang", default="en", choices=["ua", "en", "fr"])
    args = parser.parse_args()
    
    # Data
    timers = get_all_timers()
    price = get_btc_price()
    stats = calculate_cycle_stats()
    bar, percent = get_progress_bar()

    # Console output
    render_cli(timers, price=price, lang=args.lang)

    # Telegram
    if input("Send to Telegram? (y/n): ").lower() == "y":
        send_telegram_message(
            timers=timers,
            price=price,
            stats=stats,
            progress=percent,
            lang=args.lang
        )

# Export functions
__all__ = ['main']
