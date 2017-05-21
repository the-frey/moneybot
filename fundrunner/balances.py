class Balances(object):
    # balances = { 'COIN': coin_amt }
    def __init__(self, time, balances):
        self.balances = balances
        self.time     = time
        
    def __getitem__ (self, key):
        return self.balances[key]
    
    def held_coins (self):
        return [k  for k in self.balances.keys() 
                if self.balances[k] > 0 ]
    
    def to_influx_point (self):
        return {
            'measurement': 'balance',
            'time': self.time,
            'fields': self.balances,
        }

    # self, Purchase -> Balance
    def apply_purchases (self, time, purchases, fiat='BTC'):
        new_balances = self.balances.copy()
        total_fiat_investment = sum([p.investment_fiat 
                                     for p in purchases])
        new_balances[fiat] = self.balances[fiat] - total_fiat_investment
        for coin, amount, _ in purchases:
            if coin not in new_balances:
                new_balances[coin] = 0
            new_balances[coin] += amount
        return Balances(time, new_balances)

    def estimate_value (self, charts):
        remove = []
        value = 0
        for coin, amount_held in self.balances.items():
            try:
                value += charts[coin]['close'] * amount_held
            except KeyError:
                # Remove the coin -- it has been delisted.
                remove.append(coin)
        for removal in remove:
            self.balances.pop(removal)
        return value

    # Balances.from_poloniex(poloniex_client)
    def from_poloniex(poloniex_client):
        # to implement
        pass
