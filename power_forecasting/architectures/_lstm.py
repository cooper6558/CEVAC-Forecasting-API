"""
LSTM Architecture file
"""

from power_forecasting.architectures._architecture import Architecture
import tensorflow as tf
import pickle
import pandas as pd
import os
from sklearn.utils.testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# just trying to get TensorFlow to shut up
tf.get_logger().setLevel("ERROR")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
pd.set_option("mode.chained_assignment", None)


class LSTM(Architecture):
    """
    LSTM Architecture class
    """

    def __init__(self, building_name: str, building_path: str) -> None:
        """
        Initiate an LSTM architecture with model structure, parameters, & data
        :param building_name: specific building name;
            capitalization insensitive
        :param building_path: path to the building's directory
        """
        super().__init__(building_name, building_path)

        with open(f"{building_path}/LSTM/scale.pkl", "rb") as file:
            self.scale = pickle.load(file)

        self.model = tf.keras.models.load_model(f"{building_path}/LSTM/model")

    # TODO: move this decorator to the impute function
    @ignore_warnings(category=ConvergenceWarning)
    def predict(
            self,
            start_date: pd.Timestamp,
            future_range: pd.Timedelta,
            historical_data: pd.DataFrame,
            future_data: pd.DataFrame,
            verbose: bool
    ):
        """
        Produce a dynamic forecast by recursively generating step forecasts.
        :param start_date: start of forecast
        :param future_range: range of future (predicted) data required
        :param historical_data: historical data for forecast
        :param future_data: future (predicted) data for forecast
        :param verbose: whether to print forecasting progress
        :return: time series of power consumption forecast
        """
