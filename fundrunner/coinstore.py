
class LiveCoinStore(HistoricalCoinStore):
    def __init__(self, influx_client, market):
        self.market = market
        self.client = influx_client

    def latest_chart_data(self, time=''):
        return self.market.latest_chart_data()

    def btc_price (self, time=''):
        rate = requests.get('https://api.gemini.com/v1/pubticker/btcusd').json()
        return (float(rate['bid'])+float(rate['ask']))/2
