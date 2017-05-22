from .strategy import Strategy
from .. import Trade

class BuffedCoinStrategy(Strategy):
  # SALE_THRESHOLD = 0.01 # fiat value, under which we shouldn't bother selling

  def is_buffed_mean(self, coin, current_balances, current_chart_data, threshold = 0.05):
    # TODO: change this to use diff from ideal rather than mean
    coins = current_chart_data.keys()
    total_value = current_balances.estimate_value(current_chart_data)
    pct_value = (current_balances[coin] * current_chart_data[coin]['close']) / total_value
    pct_ideal = (1.0 / len(coins))
    return abs(pct_value - pct_ideal) > threshold

  def get_trades (self, current_chart_data, current_balances, fiat='BTC'):
    coins = set(current_chart_data.keys())
    held_and_valid_coins = set(current_balances.held_coins()).intersection(coins)
    buffed_coins = [
      coin for coin in held_and_valid_coins
      if self.is_buffed_mean(coin, current_balances, current_chart_data)
    ]
    # Note: Below estimates the trades, might not reflect real trades/purchases.
    total_value = current_balances.estimate_value(current_chart_data)
    ideal_value_fiat = total_value / len(coins)
    trades_to_fiat = [ Trade(coin, current_balances[coin] - ideal_value_fiat, fiat)
               for coin in buffed_coins if coin != fiat ]
    fiat_purchases = [self.get_purchase_amounts(current_chart_data, trade) for trade in trades_to_fiat]
    est_bals_after_fiat_trades = current_balances.apply_purchases(None, fiat_purchases)
    # print('est vals after fiat trades', est_bals_after_fiat_trades.balances)

    trades_from_fiat = []
    if fiat in buffed_coins:
      fiat_after_trades = est_bals_after_fiat_trades[fiat]
      coins_to_buy = coins - set([fiat])
      to_redistribute = fiat_after_trades - ideal_value_fiat 
      to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
      for coin in coins_to_buy:
        # fiat_to_sell = ideal_value_fiat * current_chart_data[coin]['close'] - est_bals_after_fiat_trades[coin]
        # price_of_coin_to_sell = current_chart_data[coin]['close']
        # amount_to_hold = ideal_value_fiat / price_of_coin_to_sell
        # amount_to_sell = est_bals_after_fiat_trades[coin] - amount_to_hold
        # print('coin, ideal, tosell', coin, ideal_value_fiat, fiat_to_sell)
        # if fiat_to_sell > SALE_THRESHOLD:
        trades_from_fiat.append(Trade(fiat, to_redistribute_per_coin, coin))
    print('purchases_from_fiat', trades_from_fiat)
  
    return trades_to_fiat + trades_from_fiat 
