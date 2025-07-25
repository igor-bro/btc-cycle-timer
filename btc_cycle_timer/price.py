#price.py 
import requests

def get_btc_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return float(response.json()["price"])
    except Exception as e:
        return f"⚠️ Error: {e}"

