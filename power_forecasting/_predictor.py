"""
Contains the Predictor class, which compiles architecture and building
information, loads data from the SQL Server, interprets the model files, and
provides a forecast function.
"""

import pandas as pd
from power_forecasting.architectures import Architecture
from power_forecasting.buildings import Building


class Predictor:
    """
    Predictor class that loads data and models, and provides forecast function.
    """

    def __init__(
            self,
            architecture: Architecture,
            building: Building
    ):
        self.building: Building = building.__init__()
        self.architecture: Architecture = architecture.__init__(
            self.building.name,
            self.building.path
        )

    def forecast(
            self,
            start_date: pd.Timestamp = None,
            future_range: pd.Timedelta = None,
            historical_data: pd.DataFrame = None,
            future_data: pd.DataFrame = None
    ) -> pd.Series:
        """
        Forecast power consumption.
        :param start_date: start of forecast
        :param future_range: range of future (predicted) data required
        :param historical_data: historical data for forecast
            (overrides data fetched by Predictor() initialization)
        :param future_data: future (predicted) data for forecast
            (overrides data fetched by Predictor() initialization)
        :return: time series of power consumption forecast
        """
        return self.architecture.predict(
            start_date,
            future_range,
            historical_data,
            future_data
        )
