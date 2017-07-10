from datetime import datetime
import json
from typing import Dict, List
import pandas as pd


class MarketHistoryMock:

    _history = json.load(open('tests/mock-data/history.json', 'r'))
    _charts = json.load(open('tests/mock-data/charts.json', 'r'))

    def latest(self, time: datetime) -> Dict[str, Dict[str, float]]:
        return self._charts[f'{time!s}']

    def asset_history(
        self,
        time: str,
        base: str,
        quote: str,
        days_back=30,
        key='price_usd',
    ) -> List[float]:
        parsed_dict = self._history[f'{time!s}-{base}-{quote}']
        # HACK marshalling HACK
        # 1. reset index of parsed dict
        # 2. transpose from a row to a column
        # 3. reverse that column
        df = pd.DataFrame(parsed_dict, index=[0]).transpose().iloc[::-1]
        return df
