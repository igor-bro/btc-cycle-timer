# price.py

import os
import pandas as pd
import requests
from datetime import datetime
from .config import BINANCE_URL, SYMBOL, INTERVAL, LIMIT  

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_btc_price():
    """
    Повертає актуальну ціну BTC (Binance API), або останню з CSV.
    """
    try:
        params = {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "limit": 1
        }
        response = requests.get(BINANCE_URL, params=params, timeout=5)
        response.raise_for_status()
        kline = response.json()[0]
        price = float(kline[4])
        return price
    except requests.RequestException as e:
        print(f"⚠️ Binance API недоступний: {e}")
    except (KeyError, IndexError, ValueError) as e:
        print(f"⚠️ Помилка обробки даних API: {e}")
    except Exception as e:
        print(f"⚠️ Неочікувана помилка: {e}")
    
            # If API is unavailable — take the last price from CSV
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.startswith("btc_price_") and f.endswith(".csv")]
        dfs = []
        for f in files:
            df = pd.read_csv(os.path.join(DATA_DIR, f))
            if "close" in df.columns:
                df = df.rename(columns={"close": "price"})
            dfs.append(df)
        if dfs:
            all_df = pd.concat(dfs).sort_values("date")
            return float(all_df["price"].iloc[-1])
    except Exception as e:
        print(f"⚠️ Помилка завантаження CSV даних: {e}")
    
    return None

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


# Експорт функцій
__all__ = ['get_btc_price', 'fetch_btc_data']

if __name__ == "__main__":
    # Collect data from 2020 to 2025
    fetch_btc_data(start_year=2020, end_year=2025)
