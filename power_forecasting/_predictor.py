"""
Contains the Predictor class, which compiles architecture and building
information, loads data from the SQL Server, interprets the model files, and
provides a forecast function.
"""

import pandas as pd
from typing import Type
from power_forecasting.architectures import Architecture
from power_forecasting.buildings import Building
from power_forecasting._load_data import load_all_data


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
        self._building: Building = building()
        self._architecture: Architecture = architecture(
            building_name=self._building.name
        )

    # TODO: argument = symbols are not separated by spaces
    def forecast(
            self,
            start_date: pd.Timestamp = None,
            future_range: pd.Timedelta = None,
            history_range: pd.Timedelta = None,
            verbose: bool = True
    ) -> pd.Series:
        """
        Forecast power consumption.
        :param start_date: start of forecast
        :param future_range: range of future (predicted) data required
        :param history_range: range of previous data to use
        :param verbose: whether to print forecasting progress
        :return: time series of power consumption forecast
        """

        historical, future = load_all_data(
            self._building,
            start_date,
            future_range,
            history_range
        )

        return self._architecture.predict(
            historical,
            future,
            verbose
        )
