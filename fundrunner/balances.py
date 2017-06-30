class Balances(object):
    # balances = { 'COIN': coin_amt }
    def __init__(self, balances, fiat='BTC'):
        # TODO balances.balances ????????
        self.balances = balances
        self.fiat     = fiat

    def __getitem__ (self, key):
        return self.balances.get(key, 0)



