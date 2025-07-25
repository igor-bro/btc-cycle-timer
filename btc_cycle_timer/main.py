# entry point for CLI

import argparse
from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import render_cli, localize
from btc_cycle_timer.price import get_btc_price
from btc_cycle_timer.telegram import send_telegram_message
from btc_cycle_timer.calc import calculate_cycle_stats
from btc_cycle_timer.status import get_progress_bar
from btc_cycle_timer.console import console

def main():
    parser = argparse.ArgumentParser(description="BTC Cycle CLI")
    parser.add_argument("--lang", default="ua", choices=["ua", "en", "fr"])
    args = parser.parse_args()
    
    # Отримати і вивести таймери
    data = get_all_timers()
    render_cli(data, lang=args.lang)

    # Прогрес-бар циклу
    bar, percent = get_progress_bar()
    console.print(f"{localize('progress.title', args.lang)}: {percent}%")
    console.print(f"[green]{bar}[/green]")

    # Поточна ціна BTC
    price = get_btc_price()
    console.print(f"\n💰 {localize('price.current', args.lang)}: ${price}")

    # Додаткова статистика циклу
    stats = calculate_cycle_stats()
    for k, v in stats.items():
        console.print(f"{k.capitalize()}: {v}")

    # Надіслати в Telegram?
    if input("Send to Telegram? (y/n): ").lower() == "y":
        send_telegram_message(data, price, lang=args.lang)
