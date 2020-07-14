"""
Contains the Predictor class, which compiles architecture and building
information, loads data from the SQL Server, interprets the model files, and
provides a forecast function.
"""

import pandas as pd
from typing import Type
from power_forecasting.architectures import Architecture
from power_forecasting.buildings import Building


class Predictor:
    """
    Predictor class that loads data and models, and provides forecast function.
    """

    def __init__(
            self,
            architecture: Type[Architecture],
            building: Type[Building]
    ) -> None:
        """
        Initiate a predictor object
        :param architecture: desired model architecture
        :param building: desired building for which to produce a forecast
        """
        self.building: Building = building()
        self.architecture: Architecture = architecture(
            building_path=self.building.path,
            building_name=self.building.name
        )

    def forecast(
            self,
            start_date: pd.Timestamp = None,
            future_range: pd.Timedelta = None,
            historical_data: pd.DataFrame = None,
            future_data: pd.DataFrame = None,
            verbose: bool = True
    ) -> pd.Series:
        """
        Forecast power consumption.
        :param start_date: start of forecast
        :param future_range: range of future (predicted) data required
        :param historical_data: historical data for forecast
            (overrides data fetched by Predictor() initialization)
        :param future_data: future (predicted) data for forecast
            (overrides data fetched by Predictor() initialization)
        :param verbose: whether to print forecasting progress
        :return: time series of power consumption forecast
        """
        return self.architecture.predict(
            start_date,
            future_range,
            historical_data,
            future_data,
            verbose
        )
