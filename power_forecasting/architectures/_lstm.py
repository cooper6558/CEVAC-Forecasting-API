"""
LSTM Architecture file
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

DIFF_PERIODS: int = 7 * 24


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
        # reindex the data
        historical_data = reindex(historical_data)
        future_data = reindex(future_data)

        # check for missing data and fill it in
        if verbose:
            print("Filling missing data")
        historical_data = impute(historical_data)
        future_data = impute(future_data)

        # add fourier indicators
        if verbose:
            print("Adding datetime indicators")
        historical_data["sin(day)"] = sin(historical_data.index.dayofyear, 365)
        historical_data["cos(day)"] = cos(historical_data.index.dayofyear, 365)
        historical_data["sin(hour)"] = sin(historical_data.index.hour, 24)
        historical_data["cos(hour)"] = cos(historical_data.index.hour, 24)
        future_data["sin(day)"] = sin(future_data.index.dayofyear, 365)
        future_data["cos(day)"] = cos(future_data.index.dayofyear, 365)
        future_data["sin(hour)"] = sin(future_data.index.hour, 24)
        future_data["cos(hour)"] = cos(future_data.index.hour, 24)

        # add weekend indicators
        # TODO: would this work without * 1?
        historical_data["Weekend"] = (historical_data.index.dayofweek < 5) * 1
        future_data["Weekend"] = (future_data.index.dayofweek < 5) * 1

        # difference power column by one week (DIFF_PERIODS = 24 * 7 hours)
        if verbose:
            print("Differencing data")
        diff_base: pd.DataFrame = historical_data.iloc[
                                  -DIFF_PERIODS:, 0
                                  ].copy()
        diff_index: pd.DatetimeIndex = pd.date_range(
            start=historical_data.index[-DIFF_PERIODS],
            end=future_data.index[-1],
            freq="h"
        )
        historical_data["Power [kW]"] = historical_data[
            "Power [kW]"
        ].diff(DIFF_PERIODS).dropna()

        # store shape of data for the model
        time_steps: int = historical_data.shape[0]
        features: int = historical_data.shape[1]
        future_range: int = future_data.shape[0]

        # scale by mean and standard deviation
        if verbose:
            print("Scaling data")
        historical_data.iloc[:, :] -= self.scale[0]
        historical_data.iloc[:, :] /= self.scale[1]
        future_data.iloc[:, :] -= self.scale[0][1:]
        future_data.iloc[:, :] /= self.scale[1][1:]

        # here is the actual forecasting algorithm
        x: np.ndarray = np.array(historical_data).reshape(
            (1, time_steps, features)
        )
        steps: pd.DataFrame = pd.DataFrame(
            index=future_data.index,
            columns={"Power [kW]", []}
        )
        digits: int = int(np.log10(future_range) + 1)
        for step in range(future_range):
            if verbose:
                if step != 0:
                    for _ in range(17 + 2 * digits):
                        print("\b", end="")
                print(
                    f"Predicting step {step:{digits}}/{future_range - 1}",
                    end=""
                )
            prediction: float = self.model.predict(x)
            steps.iloc[step] = (
                    prediction * self.scale[1][0] + self.scale[0][0]
            )[0, 0]
            new_row: np.ndarray = np.append(
                prediction, future_data.iloc[step, :].values
            )
            x = np.append(x, new_row).reshape(
                (1, time_steps + 1, features)
            )[:, 1:, :]

        # reverse differencing
        # TODO: forecast can (probably) just be a series
        if verbose:
            print("\nReversing differencing")
        forecast: pd.DataFrame = pd.DataFrame(
            columns=["Power [kW]"],
            index=diff_index
        )
        forecast.iloc[:DIFF_PERIODS] = diff_base.to_numpy().reshape(
            DIFF_PERIODS,
            1
        )
        forecast.iloc[DIFF_PERIODS:] = steps.to_numpy().reshape(
            future_range,
            1
        )
        for row in range(DIFF_PERIODS, DIFF_PERIODS + future_range):
            forecast.iloc[row] += forecast.iloc[row - DIFF_PERIODS]
        forecast = forecast[forecast.index >= future_data.index[0]]
        forecast.index.name = future_data.index.name

        return forecast["Power [kW]"]


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


def reindex(data: pd.DataFrame) -> pd.DataFrame:
    """
    Insert rows of missing data wherever index is inconsistent.
    :param data: data frame with inconsistent index
    :return: data frame with rows of missing data
    """
    index_name: str = data.index.name
    index: pd.DatetimeIndex = pd.date_range(
        data.index[0],
        data.index[-1],
        freq="h"
    )
    data = data.reindex(index)
    data.index.rename(index_name, inplace=True)
    return data


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
