# price.py

import os
import pandas as pd
import requests
from datetime import datetime
from .config import BINANCE_URL, SYMBOL, INTERVAL, LIMIT  
from btc_cycle_timer.logger import logger

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def get_btc_price():
    """
    Returns current BTC price (Binance API), or last from CSV.
    """
    logger.info("Fetching current BTC price...")
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
        logger.info(f"Fetched BTC price: {price}")
        return price
    except requests.RequestException as e:
        logger.warning(f"Binance API unavailable: {e}")
    except (KeyError, IndexError, ValueError) as e:
        logger.error(f"API data processing error: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
    
            # If API is unavailable — take the last price from CSV
    logger.info("Falling back to CSV data...")
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
            price = float(all_df["price"].iloc[-1])
            logger.info(f"Fetched BTC price from CSV: {price}")
            return price
    except Exception as e:
        logger.error(f"CSV data loading error: {e}")
    
    return None

def fetch_btc_data(start_year: int, end_year: int):
    logger.info(f"Fetching BTC data from {start_year} to {end_year}")
    
    total_files = 0
    total_records = 0
    
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
                open_price = float(kline[1])
                high = float(kline[2])
                low = float(kline[3])
                close = float(kline[4])
                volume = float(kline[5])
                all_data.append((date, open_price, high, low, close, volume))

            df = pd.DataFrame(all_data, columns=["date", "open", "high", "low", "close", "volume"])
            out_path = os.path.join(DATA_DIR, f"btc_price_{year}.csv")
            df.to_csv(out_path, index=False)

            total_files += 1
            total_records += len(df)
            print(f"✅ Loaded: {out_path} ({len(df)} records)")

        except Exception as e:
            print(f"❌ Error loading {year}: {e}")
    
    logger.info(f"Data collection completed: {total_files} files, {total_records} total records")
    return total_files, total_records

def fetch_all_historical_data():
    """
    Fetch all available historical BTC data from 2010 to current year
    """
    logger.info("Starting comprehensive historical data collection")
    
    current_year = datetime.now().year
    start_year = 2010  # Bitcoin started trading around 2010
    
    print(f"🚀 Starting comprehensive data collection from {start_year} to {current_year}")
    print("This may take several minutes...")
    
    total_files, total_records = fetch_btc_data(start_year, current_year)
    
    print(f"\n🎉 Data collection completed!")
    print(f"📊 Total files: {total_files}")
    print(f"📈 Total records: {total_records}")
    
    # Verify data integrity
    verify_data_integrity()
    
    return total_files, total_records

def verify_data_integrity():
    """
    Verify the integrity of collected data
    """
    logger.info("Verifying data integrity...")
    
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("btc_price_") and f.endswith(".csv")]
    files.sort()
    
    print(f"\n🔍 Data integrity check:")
    print(f"Found {len(files)} data files")
    
    total_records = 0
    date_range = {"min": None, "max": None}
    
    for file in files:
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, file))
            records = len(df)
            total_records += records
            
            if "date" in df.columns:
                min_date = df["date"].min()
                max_date = df["date"].max()
                
                if date_range["min"] is None or min_date < date_range["min"]:
                    date_range["min"] = min_date
                if date_range["max"] is None or max_date > date_range["max"]:
                    date_range["max"] = max_date
            
            print(f"  ✅ {file}: {records} records")
            
        except Exception as e:
            print(f"  ❌ {file}: Error - {e}")
    
    print(f"\n📊 Summary:")
    print(f"  Total records: {total_records:,}")
    print(f"  Date range: {date_range['min']} to {date_range['max']}")
    print(f"  Average records per year: {total_records // len(files) if files else 0}")
    
    logger.info(f"Data integrity check completed: {total_records} records from {date_range['min']} to {date_range['max']}")

# Export functions
__all__ = ['get_btc_price', 'fetch_btc_data']

if __name__ == "__main__":
    # Collect all available historical data
    fetch_all_historical_data()
