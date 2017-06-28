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
        self.price = None
        self.ask_amount = None
        self.bid_amount = None
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


    def __str__ (self):
        return '{!s} {!s} for {!s} {!s} (price of {!s} {!s}/{!s} on market {!s})'.format(
            self.bid_amount, self.from_coin,
            self.ask_amount, self.to_coin,
            self.price, self.from_coin, self.to_coin,
            self.market_name)


    '''
    Private methods
    '''

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


    '''
    Utility methods
    '''


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


    # Float -> Purchase
    def set_bid_amount (self, amount,
                        estimate_price_with=None):
        '''
        Set how much `from_coin` we are putting on sale, by value.

        For convenience: we can estimate the price of the asset
        to set the `ask_amount` as well.
        When `self.estimate_price_with` is passed a `chart` object,
        it will pass this down to `estimate_price()`.
        '''
        self.bid_amount = amount
        if estimate_price_with:
            self = self.estimate_price(estimate_price_with)
            self.ask_amount = self._purchase_amount(amount, self.price)
        return self


    def sell_to_achieve_value_of (self, value_in_to_coin, balances,
                                  estimate_price_with=None):
        '''
        TODO Docstring
        '''
        if estimate_price_with:
            self = self.estimate_price(estimate_price_with)
        if not self.price:
            print('ERROR: Must set a price for ProposedTrade,\
or pass a chart object into estimate_price_with')
            raise
        # After rebalance, we want the value of the coin we're trading to
        # to be equal to the ideal value (in fiat).
        # First we'll find the value of the coin we currently hold.
        # TODO balances.balances ?????
        # TODO That's a confusing-ass name
        current_from_coin_value_in_to_coin = (balances.balances[self.from_coin] * self.price)
        # To find how much coin we want to sell,
        # we'll subtract our holding's value from the ideal value
        # to produce the value of coin we must sell
        value_to_sell = current_from_coin_value_in_to_coin - value_in_to_coin
        # Now we find the amount of coin equal to this value
        amount_to_sell = value_to_sell / self.price
        self = self.set_bid_amount(amount_to_sell,
                                   estimate_price_with=estimate_price_with)
        return self


