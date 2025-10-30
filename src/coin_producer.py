import time
from quixstreams import Application
from connect_api import get_latest_coin_data

app = Application(broker_address="localhost:9092", consumer_group="coin_group")
coins_topic = app.topic(name="coins", value_serializer="json")

FIXED_RATES = {
    "SEK": 11.3,
    "NOK": 10.6,
    "DKK": 6.9,
    "EUR": 0.92
}

def main():
    with app.get_producer() as producer:
        while True:
            coin_latest = get_latest_coin_data("DOGE")

            if coin_latest is None:
                print("No data available")
                time.sleep(30)
                continue

            usd_price = coin_latest['quote']['USD']['price']
            prices_nordic = {cur: usd_price * rate for cur, rate in FIXED_RATES.items()}
            coin_latest["nordic_prices"] = prices_nordic

            kafka_message = coins_topic.serialize(
                key=coin_latest["symbol"],
                value=coin_latest
            )

            print(
                f"Producing {coin_latest['symbol']} | USD: {usd_price:,.4f} | "
                + " | ".join([f"{cur}: {price:,.4f}" for cur, price in prices_nordic.items()])
            )

            producer.produce(
                topic=coins_topic.name,
                key=kafka_message.key,
                value=kafka_message.value
            )

            time.sleep(60)


if __name__ == "__main__":
    main()
