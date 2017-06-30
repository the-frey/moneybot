from ..Strategy import Strategy


class EqualWeightIndexFund (Strategy):


    def initial_proposed_trades (self, market_state):
        '''
        "Initial" purchases are from fiat.
        (We assume funds start with only a fiat balance.)
        The resulting proposed trades should result in an equal allocation (of value, in fiat)
        across all "reachable" markets (markets in which the base currency is fiat).
        '''
        possible_investments = self._possible_investments(market_state)
        fiat_investment_per_coin = market_state.balances[self.fiat] / ( len(possible_investments) + 1.0 )
        trades = self._propose_trades_from_fiat(possible_investments,
                                                fiat_investment_per_coin,
                                                market_state)
        return trades



    def rebalancing_proposed_trades (self, coins_to_rebalance, market_state):

        possible_investments = self._possible_investments(market_state)
        total_value = market_state.estimate_total_value()
        ideal_fiat_value_per_coin = total_value / len(possible_investments)

        proposed_trades_to_fiat = list(self._propose_trades_to_fiat(coins_to_rebalance,
                                                                    ideal_fiat_value_per_coin,
                                                                    market_state))

        # Next, we will simulate actually executing all of these trades
        # Afterward, we'll get some simulated balances
        est_bals_after_fiat_trades = market_state.simulate_trades(proposed_trades_to_fiat)

        if self.fiat in coins_to_rebalance and len(proposed_trades_to_fiat) > 0:
            fiat_after_trades        = est_bals_after_fiat_trades[self.fiat]
            to_redistribute          = fiat_after_trades - ideal_fiat_value_per_coin
            coins_divested_from      = [ proposed.from_coin for proposed in proposed_trades_to_fiat]
            coins_to_buy             = possible_investments - set(coins_divested_from) - set( [self.fiat] )
            to_redistribute_per_coin = to_redistribute / len(coins_to_buy)
            proposed_trades_from_fiat = self._propose_trades_from_fiat(coins_to_buy,
                                                                       to_redistribute_per_coin,
                                                                       market_state)
            trades = proposed_trades_to_fiat + list(proposed_trades_from_fiat)

            return trades

        return proposed_trades_to_fiat
