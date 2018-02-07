from pymongo import MongoClient
from gdax import WebsocketClient

mongo_client = MongoClient('mongodb://localhost:27017/')
ltc_collection = mongo_client.crypto.ltc_eur

class RealTimeClient(WebsocketClient):

    def on_open(self):
        self.products = ["LTC-EUR"]
        self.channels = ["ticker"]
        self.mongo_collection = ltc_collection
        self.n_messages = 0

    def on_message(self, msg):
        self.n_messages += 1
        if self.mongo_collection:
            self.mongo_collection.insert_one(msg)
        if 'price' in msg and 'side' in msg:
            print ("Side:", msg["side"],
                   "\t@ {:.3f}".format(float(msg["price"])))

    # def on_error(self, e, data=None):
    #     print('Warning : {0} - data: {1}'.format(e, data))



def bollinger_bands(prices, window, n_sigma=2):
    mu = prices.rolling(window=window).mean()
    sigma = prices.rolling(window=window).std()
    up = mu + n_sigma * sigma
    low = mu - n_sigma * sigma
    return mu, up, low


if __name__ == '__main__':
    cli = RealTimeClient()
    cli.start()


    df = DataFrame([t for t in ltc_collection.find() if t["type"] == "ticker"])
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

    df.index = pandas.to_datetime(df["time"])

    s = df["price"][1:]

    dohlc = s.resample("15T").agg(["first", "max", "min", "last"])
    dohlc.columns = ["open", "high", "low", "close"]
