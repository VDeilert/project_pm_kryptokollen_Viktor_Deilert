from requests import Session, ConnectionError, Timeout, TooManyRedirects
import json
from constants import COINMARKET_API


def get_latest_coin_data(symbol="BTC"):
    API_KEY = COINMARKET_API
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {"symbol": symbol, "convert": "USD"}
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }


    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text).get("data")
        if data:
            return data.get(symbol)
        return None
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(f"API request failed: {e}")
        return None



