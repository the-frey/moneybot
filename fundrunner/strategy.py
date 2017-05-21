from . import Purchase

class Strategy (object):
    def __init__ (self, coinstore, initial_balances, start_time, end_time, 
                  fiat='BTC'):
        self.start_time = start_time
        self.end_time = end_time
        self.fiat = fiat
        self.coinstore = coinstore
        self.balances = initial_balances
        
    def step (self, time):
        charts = self.coinstore.see_available_coins(time)
        trades = self.get_trades(charts, self.balances)
        purchases = [self.get_purchase_amounts(charts, trade) for trade in trades]
        self.balances = self.balances.apply_purchases(time, purchases)
        value = self.balances.estimate_value(charts)
        return self.balances, value

    def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
        raise NotImplementedError
    
    def get_purchase_amounts (self, current_chart_data, trade, fee=0.0025):
        coin_close = current_chart_data[trade.coin]['close']
        investment = trade.investment_fiat - (trade.investment_fiat * fee)
        amount = investment / coin_close 
        return Purchase(trade.coin, amount, trade.investment_fiat)
