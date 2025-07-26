# price.py

import os
import pandas as pd
import requests
from datetime import datetime

BINANCE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "1d"
LIMIT = 366  

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_btc_data(start_year: int, end_year: int):
    for year in range(start_year, end_year + 1):
        print(f"🔄 Loading {year}...")

        start_time = int(datetime(year, 1, 1).timestamp() * 1000)
        end_time = int(datetime(year + 1, 1, 1).timestamp() * 1000)

        try:
            params = {
                "symbol": SYMBOL,
                "interval": INTERVAL,
                "startTime": start_time,
                "endTime": end_time,
                "limit": LIMIT
            }

            response = requests.get(BINANCE_URL, params=params, timeout=10)
            response.raise_for_status()
            klines = response.json()

            if not klines:
                print(f"⚠️ No data for {year}")
                continue

            all_data = []
            for kline in klines:
                ts = int(kline[0]) // 1000
                date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
                close = float(kline[4])
                all_data.append((date, close))

            df = pd.DataFrame(all_data, columns=["date", "close"])
            out_path = os.path.join(DATA_DIR, f"btc_price_{year}.csv")
            df.to_csv(out_path, index=False)

            print(f"✅ Loaded: {out_path}")

        except Exception as e:
            print(f"❌ Error loading {year}: {e}")


if __name__ == "__main__":
    # Збираємо дані з 2020 по 2025 рік
    fetch_btc_data(start_year=2020, end_year=2025)
