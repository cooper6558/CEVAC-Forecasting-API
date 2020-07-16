"""
Unittest for predictor
"""

import unittest
from power_forecasting.architectures import LSTM
from power_forecasting.buildings import Watt
import pandas as pd


class Predictor(unittest.TestCase):
    from power_forecasting import _predictor as predictor
    def setUp(self) -> None:
        self.model = self.predictor.Predictor(
            building=Watt,
            architecture=LSTM
        )
    def test_forecast(self):
        print(self.model.forecast(
            start_date=pd.Timestamp("2019-11-11")
        ))


if __name__ == '__main__':
    unittest.main()
