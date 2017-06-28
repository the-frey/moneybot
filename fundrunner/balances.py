class Balances(object):
    # balances = { 'COIN': coin_amt }
    def __init__(self, balances, fiat='BTC'):
        self.balances = balances
        self.fiat     = fiat

    def __getitem__ (self, key):
        return self.balances.get(key, 0)

    def held_coins (self):
        return [k  for k in self.balances.keys()
                if self.balances[k] > 0 ]


    # TODO This should be called simulate_purchases
    def apply_purchases (self, proposed_trades):
        '''
        This method sanity-checks all proposed purchases,
        before shipping them off to the backtest / live-market.
        '''
        new_balances = self.balances.copy()
        for proposed in proposed_trades:
            # Check that we have enough to sell:
            if proposed.bid_amount > \
                 new_balances[proposed.from_coin]:
                # If we don't,
                # We will just sell what's available and move on.
                proposed.bid_amount = new_balances[proposed.from_coin]
            # If we pass these conditions, we can sell
            new_balances[proposed.from_coin] -= proposed.bid_amount
            if proposed.to_coin not in new_balances:
                new_balances[proposed.to_coin] = 0
            # TODO we can get fancier with this later,
            # observe trends in actual trades we propose vs execute,
            # and use that to make more realistic simulations~!
            # (after all, our proposed price will not always be achievable)
            est_trade_amt = proposed.bid_amount / proposed.price
            new_balances[proposed.to_coin] += est_trade_amt
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
