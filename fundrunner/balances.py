class Balances(object):
    # balances = { 'COIN': coin_amt }
    def __init__(self, time, balances):
        self.balances = balances
        self.time     = time
        
    def __getitem__ (self, key):
        return self.balances.get(key, 0)

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
    def apply_purchases (self, time, purchases):
        new_balances = self.balances.copy()
        for from_coin, from_amount, to_coin, to_amount in purchases:
            new_balances[from_coin] -= from_amount
            if to_coin not in new_balances:
                new_balances[to_coin] = 0
            new_balances[to_coin] += to_amount
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
