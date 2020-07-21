"""LSTM Architecture file
"""

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from power_forecasting.architectures._architecture import Architecture
import tensorflow as tf
from tensorflow.keras.models import Sequential
import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import numpy as np

tf.get_logger().setLevel("ERROR")
DIFF_PERIODS: int = 7 * 24


class LSTM(Architecture):
    """
    LSTM Architecture class
    """

    def __init__(self, building_name: str) -> None:
        """
        Initiate an LSTM architecture with model structure, parameters, & data
        :param building_name: specific building name;
            capitalization insensitive
        """
        super().__init__(building_name)

        with open(f"{self.path}lstm/scale.pkl", "rb") as file:
            self.scale = pickle.load(file)

        self.model = tf.keras.models.load_model(
            f"{self.path}lstm/model"
        )

    # TODO: split this into smaller functions
    def predict(
            self,
            historical_data: pd.DataFrame,
            future_data: pd.DataFrame,
            verbose: bool
    ) -> pd.Series:
        """
        Produce a dynamic forecast by recursively generating step forecasts.
        === ASSUMPTIONS ==
         - future_data is missing first column of historical_data;
         - both indexes are DateTime
         - data is hourly & consecutive, even across data frames
            (although some values can be missing, the index must be continuous)
         - column names should be the same between both data frames
        :param historical_data: historical data for forecast
        :param future_data: future (predicted) data for forecast
        :param verbose: whether to print forecasting progress
        :return: time series of power consumption forecast
        """

        # check for missing data and fill it in
        if verbose:
            print("Filling missing data")
        historical_data = impute(historical_data)
        future_data = impute(future_data)
        data = pd.concat([historical_data, future_data])

        # difference data
        # TODO: is copy() necessary?
        if verbose:
            print("Differencing data")
        diff_base: pd.Series = historical_data.iloc[-DIFF_PERIODS:, 0].copy()
        data = data.diff(DIFF_PERIODS)
        data.dropna(inplace=True, how="all")

        # add fourier indicators
        if verbose:
            print("Adding datetime indicators")
        data["sin(day)"] = sin(data.index.dayofyear, 365)
        data["cos(day)"] = cos(data.index.dayofyear, 365)
        data["sin(hour)"] = sin(data.index.hour, 24)
        data["cos(hour)"] = cos(data.index.hour, 24)

        # add weekend indicators
        # this is inverted; it should be >= 5, not < 5.
        # I made the same mistake training the model, so it's actually correct.
        data["Weekend"] = data.index.dayofweek < 5
        features: int = data.shape[1]
        future_range: int = future_data.shape[0]
        time_steps: int = historical_data.shape[0] - DIFF_PERIODS

        # scale by mean and standard deviation
        # TODO: does this work without iloc?
        if verbose:
            print("Scaling data")
        data.iloc[:, :] -= self.scale[0]
        data.iloc[:, :] /= self.scale[1]

        # here is the actual forecasting algorithm
        x: np.ndarray = data.iloc[:time_steps, :].to_numpy().reshape(
            (1, time_steps, features)
        )
        # store predicted differences
        steps: pd.Series = pd.Series(
            index=future_data.index,
            dtype="float64"
        )
        digits: int = int(np.log10(future_range) + 1)
        for step in range(future_range):
            if verbose:
                if step != 0:
                    for _ in range(17 + 2 * digits):
                        print("\b", end="")
                print(
                    f"Predicting step {step + 1:{digits}}/{future_range}",
                    end=""
                )
            prediction: float = self.model.predict(x).reshape(1)
            steps[step] = prediction
            # TODO: can this work without .values?
            new_row: np.ndarray = np.append(
                prediction, data.iloc[step + time_steps, 1:].values
            )
            x = np.append(x, new_row).reshape(
                (1, time_steps + 1, features)
            )[:, 1:, :]

        # reverse scaling
        if verbose:
            print("\nReversing scaling")
        steps *= self.scale[1][0]
        steps += self.scale[0][0]

        # reverse differencing
        if verbose:
            print("Reversing differencing")
        forecast: pd.Series = pd.Series(
            name=data.columns[0],
            index=data.index,
            dtype="float64"
        )
        forecast.iloc[:DIFF_PERIODS] = diff_base
        forecast.iloc[DIFF_PERIODS:] = steps
        for row in range(DIFF_PERIODS, DIFF_PERIODS + future_range):
            forecast.iloc[row] += forecast.iloc[row - DIFF_PERIODS]
        forecast = forecast[forecast.index >= future_data.index[0]]

        return forecast


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

    data.iloc[:, :] = scaler.fit_transform(data)
    n = np.min(data.count())
    imputer = IterativeImputer(
        estimator=KNeighborsRegressor(n_neighbors=n),
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


# TODO: put this before impute for readability


def sin(series: np.ndarray, offset: float) -> np.ndarray:
    """
    Produce a sine wave.
    :param series: x axis values
    :param offset: x axis scale
    :return: sine wave of series
    """
    return np.sin(2 * np.pi * series / offset)


def cos(series: np.ndarray, offset: float) -> np.ndarray:
    """
    Produce a cosine wave.
    :param series: x axis values
    :param offset: x axis scale
    :return: cosine wave of series
    """
    return np.cos(2 * np.pi * series / offset)
