import datetime

from krakenex import API
from pandas import DataFrame

KEY_PATH = "kraken.key"
COLUMNS = ["timestamp", "open", "high", "low", "close", "vwap", "volume", "count" ]
PAIR = "XXBTZEUR"



def get_kraken_prices(save_path, interval=24*60, pair=PAIR):
    date_format = "%Y-%m-%d %H:%M:%S"

    api = API()
    api.load_key(KEY_PATH)

    req = {"pair" : pair,  "interval":interval}
    res = api.query_public(method="OHLC", req=req)

    df = DataFrame(res["result"][pair])
    df.columns = COLUMNS

    df["time"] = df["timestamp"].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime(date_format))

    df.to_csv(save_path, index=False, encoding="utf-8", sep="\t")
