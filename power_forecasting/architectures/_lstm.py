"""
LSTM Architecture file
"""

from power_forecasting.architectures._architecture import Architecture
import tensorflow as tf
from tensorflow.keras.models import Sequential
import pickle
import pandas as pd
import os
from sklearn.utils.testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
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
            self.scale: tuple = pickle.load(file)

        self.model: Sequential = tf.keras.models.load_model(
            f"{building_path}/LSTM/model"
        )

    # TODO: move this decorator to the impute function
    @ignore_warnings(category=ConvergenceWarning)
    def predict(
            self,
            historical_data: pd.DataFrame,
            future_data: pd.DataFrame,
            verbose: bool
    ) -> pd.Series:
        """
        Produce a dynamic forecast by recursively generating step forecasts.
        :param historical_data: historical data for forecast
        :param future_data: future (predicted) data for forecast
        :param verbose: whether to print forecasting progress
        :return: time series of power consumption forecast
        """


def impute(data: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing data.
    :param data: data frame with missing values
    :return: the same data frame, with missing values filled in
    """
    scaler: StandardScaler = StandardScaler()
    base_date: pd.Timestamp = data.index[0]

    data["Days"] = data.index.map(
        lambda date: (date - base_date).days
    )

    # TODO: would this work without iloc?
    data.iloc[:, :] = scaler.fit_transform(data)

    imputer: IterativeImputer = IterativeImputer(
        estimator=KNeighborsRegressor(n_neighbors=30),
        max_iter=10,
        verbose=0
    )

    imputed_data: pd.DataFrame = pd.DataFrame(
        columns=list(data.columns),
        index=data.index
    )

    imputed_data.iloc[:, :] = imputer.fit_transform(data.iloc[:, :])
    imputed_data.iloc[:, :] = scaler.inverse_transform(imputed_data.iloc[:, :])
    return imputed_data.drop(columns=["Days"])
