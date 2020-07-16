"""
Contains the Predictor class, which compiles architecture and building
information, loads data from the SQL Server, interprets the model files, and
provides a forecast function.
"""

import pandas as pd
import numpy as np
from typing import Type
from power_forecasting.architectures import Architecture
from power_forecasting.buildings import Building
# TODO: put group_by_hour in _predictor.py
from power_forecasting._load_data import (
    load_historical_data,
    load_future_data,
    group_by_hour
)


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
    # args: start_date, future_range, history_range, future_data, verbose
    def forecast(
            self,
            start_date: pd.Timestamp = None,
            future_range: pd.Timedelta = None,
            history_range: pd.Timedelta = None,
            future_data: pd.DataFrame = None,
            verbose: bool = True
    ) -> pd.Series:
        """
        Forecast power consumption.
        :param start_date: start of forecast
        :param future_range: range of future (predicted) data required
        :param history_range: range of previous data to use
        :param future_data: future (predicted) data for forecast
            (overrides data fetched by Predictor() initialization)
        :param verbose: whether to print forecasting progress
        :return: time series of power consumption forecast
        """
        data: pd.DataFrame = load_historical_data(
            self._building
        )
        if start_date is None:
            start_date = data.index[-1] + pd.Timedelta(hours=1)

        if future_range is None:
            future_range = pd.Timedelta(days=1)

        if history_range is None:
            history_range = pd.Timedelta(weeks=2)

        if future_data is None:
            future_data = data.copy()
        else:
            # TODO: is there a more "Pythonic" way to do this?
            for column in future_data:
                future_data[column] = group_by_hour(future_data[column])
        future_data = future_data.reindex(pd.date_range(
            start_date,
            start_date + future_range - pd.Timedelta(hours=1),
            freq="h",
            name=future_data.index.name
        ))

        future_data.fillna(
            load_future_data(self._building, future_range),
            inplace=True
        )

        historical_data: pd.DataFrame = data.copy()
        historical_data = historical_data.reindex(pd.date_range(
            start_date - history_range,
            start_date - pd.Timedelta(hours=1),
            freq="h",
            name=historical_data.index.name
        ))

        # TODO: there has to be a better way to do this
        for dataframe in (historical_data, future_data):
            for column in dataframe:
                if dataframe[column].isna().all():
                    raise IndexError("No column may be entirely NaN")

        # TODO: this should just be a testing feature
        future_data = future_data.mask(
            np.random.random(future_data.shape) < .2
        )
        print(historical_data)
        print(future_data)
        return self._architecture.predict(
            historical_data,
            future_data,
            verbose
        )
