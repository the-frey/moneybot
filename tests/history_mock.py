from datetime import datetime
import pickle
from typing import Dict, List


class MarketHistoryMock:

    def lookup(self, pckl, key):
        with open(pckl, 'rb') as handle:
            d = pickle.load(handle)
            return d[key]

    def latest(self, time: datetime) -> Dict[str, Dict[str, float]]:
        return self.lookup(
            'tests/mock-data/charts.pickle',
            f'{time!s}'
        )

    def asset_history(
        self,
        time: str,
        base: str,
        quote: str,
        days_back=30,
        key='price_usd',
    ) -> List[float]:
        return self.lookup(
            'tests/mock-data/history.pickle',
            f'{time!s}-{base}-{quote}'
        )
