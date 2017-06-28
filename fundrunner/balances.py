class Balances(object):
    # balances = { 'COIN': coin_amt }
    def __init__(self, balances, fiat='BTC'):
        # TODO balances.balances ????????
        self.balances = balances
        self.fiat     = fiat

    def __getitem__ (self, key):
        return self.balances.get(key, 0)

    def held_coins (self):
        return [k  for k in self.balances.keys()
                if self.balances[k] > 0 ]


    # TODO Clearly this should be in a MarketAdapter
    def simulate (self, proposed, new_balances):
        '''
        TODO Docstring

        TODO State assumptions going into this simulation

        We can get fancier with this later,
        observe trends in actual trades we propose vs execute,
        and use that to make more realistic simulations~!
        (after all, our proposed price will not always be achievable)
        '''
        # TODO This makes sense as logic, but new_balances is confusing
        new_balances[proposed.from_coin] -= proposed.bid_amount
        if proposed.to_coin not in new_balances:
            new_balances[proposed.to_coin] = 0
        est_trade_amt = proposed.bid_amount / proposed.price
        new_balances[proposed.to_coin] += est_trade_amt
        return new_balances


    # TODO Not sure this method should even exist.
    #       MarketAdapter could have a method execute_trades()
    #       that processes each trade in order, updating its Balance as it goes.
    #       if that's explicit,
    #       we can just overwrite some execute() method
    #       for whatever market / backtest stiuation......
    def apply_purchases (self, proposed_trades):
        '''
        This method sanity-checks all proposed purchases,
        before shipping them off to the backtest / live-market.
        '''
        # TODO I hate copying this
        new_balances = self.balances.copy()
        for proposed in proposed_trades:

            # TODO Where should this check / mutation go?
            #      Don't want duplication between simulating purchases
            #      and actually performing them.
            #      perhaps one method should filter illegal trades,
            #      and coerce them into legal trades,
            #      depending on what's necessary

            # Check that we have enough to sell:
            if proposed.bid_amount > \
                 new_balances[proposed.from_coin]:
                # If we don't,
                # We will just sell what's available and move on.
                proposed.bid_amount = new_balances[proposed.from_coin]

            # Actually simulate purchase of the proposed trade
            # TODO I hate mutating stuff out of scope, my god
            new_balances = self.simulate(proposed, new_balances)

        return Balances(new_balances)

    # self, charts -> Dict
    def estimate_values (self, charts, key='weightedAverage'):
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
                    fiat_price = float(charts[relevant_market][key])
                    fiat_values[coin] =  fiat_price * amount_held
            except KeyError:
                # Remove the coin -- it has been delisted.
                remove.append(coin)
        for removal in remove:
            self.balances.pop(removal)
        return fiat_values

    def estimate_total_fiat_value (self, charts):
        vs = self.estimate_values(charts)
        return sum(vs.values())
