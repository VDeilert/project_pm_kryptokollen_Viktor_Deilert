from quixstreams import Application
from quixstreams.sinks.community.postgresql import PostgreSQLSink
from constants import POSTGRES_DBNAME, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER
from pprint import pprint

def extract_coin_data(message):
    usd_quote = message["quote"]["USD"]
    coin_name = message.get("name") or message.get("symbol")
    last_updated = message.get("last_updated")
    nordic_prices = message.get("nordic_prices", {})

    data = {
        "coin": coin_name,
        "price_usd": usd_quote.get("price") if usd_quote else None,
        "volume_24": usd_quote.get("volume_24h") if usd_quote else None,
        "market_cap": usd_quote.get("market_cap") if usd_quote else None,
        "percent_change_24h": usd_quote.get("percent_change_24h") if usd_quote else None,
        "updated": last_updated,
    }

    for cur in ["SEK", "NOK", "DKK", "EUR"]:
        data[f"price_{cur.lower()}"] = nordic_prices.get(cur)

    return data

def create_postgres_sink():
    return PostgreSQLSink(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DBNAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        table_name="cryptoprices",
        schema_auto_update=True,
    )

def main():
    app = Application(
        broker_address="localhost:9092",
        consumer_group="coin_group",
        auto_offset_reset="earliest"
    )

    coins_topic = app.topic(name="coins", value_deserializer="json")
    sdf = app.dataframe(topic=coins_topic)
    sdf = sdf.apply(extract_coin_data)
    sdf.update(lambda data: pprint(data))

    postgres_sink = create_postgres_sink()
    sdf.sink(postgres_sink)

    app.run()

if __name__ == "__main__":
    main()
