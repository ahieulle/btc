import datetime

from pandas import DataFrame
from gdax import PublicClient

cli = PublicClient()


def get_data(currency, granularity):
    N = 12
    date_format = "%Y-%m-%d %H:%M:%S"
    cols = [ "time", "low", "high", "open", "close", "volume" ]
    df = DataFrame(cli.get_product_historic_rates(currency, granularity=granularity))
    df.columns = cols

    df = df.sort_values("time", ascending=True)

    df["time_str"] = df["time"].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime(date_format))

    df["diff"] = df["close"] - df["open"]
    df.loc[df["diff"] > 0, "H"] = df.loc[df["diff"] > 0, "close"] - df.loc[df["diff"] > 0, "open"]
    df.loc[df["diff"] <= 0, "H"] = 0
    df.loc[df["diff"] <= 0, "B"] = df.loc[df["diff"] <= 0, "open"] - df.loc[df["diff"] <= 0, "close"]
    df.loc[df["diff"] > 0, "B"] = 0

    df["MME_H"] = df["H"].ewm(span=N, adjust=False).mean()
    df["MME_B"] = df["B"].ewm(span=N, adjust=False).mean()

    df["RSI"] = 100 * df["MME_H"] / (df["MME_H"] + df["MME_B"])

    return df


def run_strategy(currency, granularity):
    df = get_data(currency, granularity)

    pnl = 0
    holdings = 0

    for j,r in df.iterrows():
        if r["RSI"] < 20 and holdings == 0:
            p = r["close"]
            print( "BUY 1 {0} at {1}".format(crypto, p))
            holdings += 1
            pnl -= p

        elif r["RSI"] > 80 and holdings > 0:
            p = r["close"]
            print( "SELL 1 {0} at {1}".format(crypto, p))
            holdings -= 1
            pnl += p

    print( "Holdings : {0}  PNL : {1}".format(holdings, pnl))

    print(df[["close", "RSI", "time_str"]].tail())


crypto = "LTC"
fiat = "EUR"
currency = "{0}-{1}".format(crypto, fiat)
granularity = 300

run_strategy(currency, granularity)
