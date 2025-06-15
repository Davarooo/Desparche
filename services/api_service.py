# services/api_service.py

import requests

class CryptoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3/simple/price"

    def get_prices(self, crypto_ids, currency="usd"):
        params = {
            "ids": ",".join(crypto_ids),
            "vs_currencies": currency
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # lanza error si no es 200
            return response.json()
        except requests.RequestException as e:
            print("❌ Error al conectarse a CoinGecko:", e)
            return None
