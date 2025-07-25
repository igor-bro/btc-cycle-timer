# entry point for CLI

from btc_cycle_timer.timer import get_all_timers
from btc_cycle_timer.utils import render_cli
import argparse

def main():
    parser = argparse.ArgumentParser(description="BTC Cycle CLI")
    parser.add_argument("--lang", default="ua", choices=["ua", "en", "fr"])
    args = parser.parse_args()
    
    data = get_all_timers()
    render_cli(data, lang=args.lang)
