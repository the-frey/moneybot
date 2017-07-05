class MarketState (object):

    '''
    TODO Docstring
    '''

    def __init__ (self, chart_data, balances, time, fiat):
        self.chart_data = chart_data
        self.balances = balances
        self.time = time
        self.fiat = fiat


    '''
    Private methods
    '''

    def _held_coins (self):
        return [k  for k in self.balances.keys()
                if self.balances[k] > 0 ]


    def _coin_names (self, market_name):
        coins = market_name.split('_')
        return coins[0], coins[1]


    def _available_markets (self):
        return set([ k for k in self.chart_data.keys()
                     if k.startswith(self.fiat) ])


    '''
    Public methods
    '''

    # String -> Float
    def balance (self, coin):
        '''
        Returns the quantity of a coin held.
        '''
        return self.balances[coin]


    # String -> Float
    def price (self, market,
               key='weightedAverage'):
        '''
        Returns the price of a market, in terms of the base asset.
        '''
        return float(self.chart_data[market][key])


    # String -> Bool
    def only_holding (self, coin):
        '''
        Returns true if the only thing we are holding is `coin`
        '''
        return self._held_coins() == [ coin ]


    # MarketState -> Set<String>
    def available_coins (self):
        markets = self._available_markets()
        return set([ self._coin_names(market)[1]
                     for market in markets ] + [ self.fiat ])


    def held_coins_with_chart_data (self):
        avail_coins = self.available_coins()
        return set(self._held_coins()).intersection(avail_coins)


    def estimate_values (self, **kwargs):
        '''
        Returns a dict where keys are coin names,
        and values are the value of our holdings in fiat.
        '''
        fiat_values = {}
        remove = []
        for coin, amount_held in self.balances.items():
            try:
                if coin == self.fiat:
                    fiat_values[coin] = amount_held
                else:
                    relevant_market = '{!s}_{!s}'.format(self.fiat, coin)
                    fiat_price = self.price(relevant_market, **kwargs)
                    fiat_values[coin] =  fiat_price * amount_held
            except KeyError:
                # Remove the coin -- it has been delisted.
                remove.append(coin)
        for removal in remove:
            self.balances.pop(removal)
        return fiat_values


    # -> Float
    def estimate_total_value (self, **kwargs):
        '''
        Returns the sume of all holding values, in fiat.
        '''
        return sum(self.estimate_values(**kwargs).values())


    # -> Float
    def estimate_total_value_usd (self, **kwargs):
        '''
        Returns the sum of all holding values, in USD.
        '''
        est = self.estimate_total_value() * self.price('USD_BTC', **kwargs)
        return round(est, 2)


    # TODO Not sure this really belongs here
    #       maybe more the job of BacktestMarketAdapter
    def simulate_trades (self, proposed_trades):
        '''
        TODO Docstring

        TODO State assumptions going into this simulation

        We can get fancier with this later,
        observe trends in actual trades we propose vs execute,
        and use that to make more realistic simulations~!
        (after all, our proposed price will not always be achievable)
        '''
        def simulate (proposed, new_balances):
            # TODO This makes sense as logic, but new_balances is confusing
            new_balances[proposed.from_coin] -= proposed.bid_amount
            if proposed.to_coin not in new_balances:
                new_balances[proposed.to_coin] = 0
            est_trade_amt = proposed.bid_amount / proposed.price
            new_balances[proposed.to_coin] += est_trade_amt
            return new_balances
        '''
        This method sanity-checks all proposed purchases,
        before shipping them off to the backtest / live-market.
        '''
        # TODO I hate copying this
        new_balances = self.balances.copy()
        for proposed in proposed_trades:
            # Actually simulate purchase of the proposed trade
            # TODO I hate mutating stuff out of scope, so much
            new_balances = simulate(proposed, new_balances)

        return new_balances
