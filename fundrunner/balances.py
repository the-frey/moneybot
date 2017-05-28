class Balances(object):
    # balances = { 'COIN': coin_amt }
    def __init__(self, time, balances, fiat='BTC'):
        self.balances = balances
        self.time     = time
        self.fiat     = fiat

    def __getitem__ (self, key):
        return self.balances.get(key, 0)

    def held_coins (self):
        return [k  for k in self.balances.keys()
                if self.balances[k] > 0 ]

    # self, Purchase -> Balance
    def apply_purchases (self, time, purchases):
        new_balances = self.balances.copy()
        for from_coin, from_amount, to_coin, to_amount in purchases:
            new_balances[from_coin] -= from_amount
            if to_coin not in new_balances:
                new_balances[to_coin] = 0
            new_balances[to_coin] += to_amount
        return Balances(time, new_balances)

    def estimate_values (self, charts, key='average'):
        values = {}
        remove = []
        for coin, amount_held in self.balances.items():
            try:
                if coin == self.fiat:
                    values[coin] = amount_held
                else:
                    relevant_market = '{!s}_{!s}'.format(self.fiat, coin)
                    values[coin] = charts[relevant_market][key] * amount_held
            except KeyError:
                # Remove the coin -- it has been delisted.
                remove.append(coin)
        for removal in remove:
            self.balances.pop(removal)
        return values

    def estimate_total_fiat_value (self, charts):
        vs = self.estimate_values(charts)
        return sum(vs.values())

    # Balances.from_poloniex(poloniex_client)
    def from_poloniex(poloniex_client):
        # to implement
        pass
