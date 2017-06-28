# String, String -> String
def market_name (base, quote):
    ''' Return Poloniex market name'''
    return '{!s}_{!s}'.format(base, quote)

class ProposedTrade (object):

    def __init__ (self, from_coin, to_coin,
                  fiat='BTC', fee=0.0025):

        self.from_coin = from_coin
        self.to_coin = to_coin
        self.fiat = fiat
        self.fee = fee

        # get the Poloniex market name
        # Poloniex markets are named `{fiatSymol}_{quoteSymbol}`
        # By seeing whether from_ or to_ are the fiat,
        # we will construct the proper market name.
        # (yes, we can only trade directly fiat to/from fiat for now. sorry!)
        if from_coin == fiat:
            self.market_name = market_name(fiat, to_coin)
        elif to_coin == fiat:
            self.market_name = market_name(fiat, from_coin)

    # Float, Float -> Float
    def _purchase_amount (self, investment, price):
        '''
        Private method.
        Get the amount of some coin purchased,
        given an investment (in quote), and a price (in quote),
        accounting for trading fees.
        '''
        in_amt = investment - (investment * self.fee)
        return in_amt / price

    # ChartData -> Float
    def estimate_price (self, chart_data):
        '''
        Returns the approximate price of the quote value, given some chart data.
        '''
        base_price = float(chart_data[self.market_name]['weightedAverage'])
        if self.to_coin == self.fiat:
            self.price = (1 / base_price)
        else:
            self.price = base_price
        return self

    # def set_ask_amount (self, investment):
    #     self.ask_amount = investment
    #     self.bid_amount = self._purchase_amount(investment, self.price)
    #     return self

    # Float -> Purchase
    def set_bid_amount (self, amount):
        '''
        Set how much `from_coin` we are putting on sale.
        '''
        self.bid_amount = amount
        self.ask_amount = self._purchase_amount(amount, self.price)
        return self

    def __str__ (self):
        return '{!s} {!s} for {!s} {!s} (price of {!s} {!s}/{!s} on market {!s})'.format(
            self.bid_amount, self.from_coin,
            self.ask_amount, self.to_coin,
            self.price, self.from_coin, self.to_coin,
            self.market_name,
            )
