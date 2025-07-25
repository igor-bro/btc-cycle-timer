import requests

def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        response = requests.get(url, params=params)
        data = response.json()
        return data["bitcoin"]["usd"]
    except Exception as e:
        return f"⚠️ Error: {e}"
