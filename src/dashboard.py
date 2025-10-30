import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
import pandas as pd
from datetime import timedelta
from constants import POSTGRES_DBNAME, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER
from charts import line_chart

connection_string = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"
)
engine = create_engine(connection_string)

def load_data(query: str) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        df = df.set_index("timestamp")
        return df

def human_format(num):
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "N/A"
    for unit in ["", "K", "M", "B", "T"]:
        if abs(num) < 1000:
            return f"{num:3.2f}{unit}"
        num /= 1000
    return f"{num:.1f}P"

st_autorefresh(interval=10 * 1000, limit=100, key="data_refresh")

def layout():
    st.title("Cryptocurrency Dashboard")
    st.markdown("Live data fetched from the CoinMarketCap API")

    df = load_data("SELECT * FROM cryptoprices;")
    coins = sorted(df["coin"].unique())
    selected_coin = st.selectbox("Select cryptocurrency:", coins, index=0)
    coin_df = df[df["coin"] == selected_coin]

    latest = coin_df.iloc[-1]
    time_24h_ago = latest.name - timedelta(hours=24)
    df_24h_ago = coin_df[coin_df.index <= time_24h_ago]
    old = df_24h_ago.iloc[-1] if not df_24h_ago.empty else coin_df.iloc[0]

    currency_options = ["USD"] + [
        c.split("_")[1].upper()
        for c in coin_df.columns
        if c.startswith("price_") and not c.endswith("usd")
    ]
    selected_currency = st.selectbox("Select currency:", sorted(currency_options))
    price_col = f"price_{selected_currency.lower()}"

    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)

    price_now = latest.get(price_col)
    col1.metric(
        f"Price ({selected_currency})",
        f"{price_now:,.3f}" if price_now else "N/A"
    )

    volume_now = latest.get("volume_24")
    volume_old = old.get("volume_24")
    vol_diff = volume_now - volume_old if volume_now and volume_old else 0

    price_in_usd = latest.get("price_usd")
    exchange_rate = (
        price_now / price_in_usd
        if price_in_usd and price_now and selected_currency != "USD"
        else 1
    )

    volume_converted = volume_now * exchange_rate if volume_now else None
    vol_diff_converted = vol_diff * exchange_rate if vol_diff else None
    col2.metric(
        f"Volume (24h) ({selected_currency})",
        f"{human_format(volume_converted)}" if volume_converted else "N/A",
        f"{human_format(vol_diff_converted)}" if vol_diff_converted else "N/A",
    )

    market_cap_now = latest.get("market_cap")
    market_cap_old = old.get("market_cap")
    market_cap_converted = market_cap_now * exchange_rate if market_cap_now else None
    market_cap_old_converted = market_cap_old * exchange_rate if market_cap_old else None
    market_cap_diff = (
        market_cap_converted - market_cap_old_converted
        if market_cap_converted and market_cap_old_converted
        else None
    )

    col3.metric(
        f"Market Cap ({selected_currency})",
        f"{human_format(market_cap_converted)}" if market_cap_converted else "N/A",
        f"{human_format(market_cap_diff)}" if market_cap_diff else "N/A",
    )

    percent_change = latest.get("percent_change_24h")
    col4.metric(
        "Price Change (24h)",
        f"{percent_change:.2f}%" if percent_change else "N/A",
    )

    st.subheader(f"Price over time ({selected_currency})")
    if price_col in coin_df.columns:
        coin_df["price_converted"] = coin_df[price_col]
        price_chart = line_chart(
            x=coin_df.index,
            y=coin_df["price_converted"],
            title=f"Price ({selected_currency})",
        )
        st.pyplot(price_chart)
    else:
        st.warning(f"No data available for {selected_currency}")

    st.subheader(f"Volume over time (24h, {selected_currency})")
    if "volume_24" in coin_df.columns:
        coin_df["volume_converted"] = coin_df["volume_24"] * exchange_rate
        volume_chart = line_chart(
            x=coin_df.index,
            y=coin_df["volume_converted"],
            title=f"Volume (24h, {selected_currency})",
        )
        st.pyplot(volume_chart)

    if "percent_change_24h" in coin_df.columns:
        st.subheader("Price change over time (24h %)")
        change_chart = line_chart(
            x=coin_df.index,
            y=coin_df["percent_change_24h"],
            title="Price Change 24h (%)",
        )
        st.pyplot(change_chart)

        st.subheader("Latest data")
        st.dataframe(coin_df.tail())

if __name__ == "__main__":
    layout()