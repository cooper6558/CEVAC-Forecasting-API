"""
Contains the Architecture base class, which provides a format for interpreting
models and producing forecasts. This file also contains functions to help fetch
data.
"""

import pandas as pd
import os


class Architecture:
    """
    Base class for all architectures. Mainly serves to load data.
    """

    def __init__(self, building_name: str) -> None:
        """
        Initiate an architecture object storing data required for forecasting
        :param building_name: specific building name;
            capitalization insensitive
        """
        self.path: str = (
                os.getenv("FORECAST_MODEL_DIR")
                + building_name.lower()
                + "/"
        )

    # TODO: fix these args
    def predict(self, *args) -> pd.Series:
        """
        Prototype for predict function. This is never used; only overridden.
        :return: empty time series
        """
        return pd.Series()
