"""
Contains the Architecture base class, which provides a format for interpreting
models and producing forecasts. This file also contains functions to help fetch
data.
"""

import pandas as pd
from CEVAC.Connectors import SQLConnector


class Architecture:
    """
    Base class for all architectures. Mainly serves to load data.
    """

    def __init__(self, building_name: str, building_path: str) -> None:
        """
        Initiate an architecture object storing data required for forecasting
        :param building_name: specific building name;
            capitalization insensitive
        :param building_path: path to the building's directory
        """
        self.data: pd.DataFrame
        self.date: pd.Timestamp
        self.data, self.date = load_all_data(building_name)
        self.path: str = building_path

    def predict(self, *args) -> pd.Series:
        """
        Prototype for predict function. This is never used; only overridden.
        :return: empty time series
        """
        self.date = args
        return pd.Series()


def load_all_data(
        building_name: str,
        future_range: pd.Timedelta = None
) -> (pd.DataFrame, pd.Timestamp):
    """
    Read from SQL Server, and compile everything into one dataframe.
    :param building_name: specific building name;
        capitalization insensitive
    :param future_range: range of future (predicted) data required;
        default 1 day
    :return: Tuple of compiled dataframe, and the current date
    """
    if future_range is None:
        future_range = pd.to_timedelta(24, unit="h")

    raw_power_data: pd.Series = get_power_data(building_name)
    start_date: pd.Timestamp = raw_power_data.index[-1]
    power: pd.Series = group_by_hour(raw_power_data)
    clouds: pd.Series = group_by_hour(get_weather_data(0))
    temperature: pd.Series = group_by_hour(get_weather_data(6))
    occupancy: pd.Series = group_by_hour(
        get_occupancy_data(
            building_name,
            future_range
        )
    )
    data: pd.DataFrame = pd.concat(
        [power, clouds, temperature, occupancy],
        axis=1
    )
    data.name = building_name

    return data, start_date


def group_by_hour(data: pd.Series) -> pd.Series:
    """
    Take a time series and produce hourly means.
    This helps "line up" real world data where observations are mismatched.
    :param data: time series, whose index is "UTCDateTime"
    :return: hourly time series
    """
    name: str = data.name
    data: pd.DataFrame = data.groupby(
        [data.index.date, data.index.hour]
    ).mean().reset_index()
    data["level_0"] = pd.to_datetime(data["level_0"])
    data["UTCDaTime"] = pd.to_timedelta(data["UTCDateTime"], unit="h")
    data["UTCDateTime"] += data["level_0"]
    return data.set_index("UTCDateTime")[name]


def get_sql(query: str) -> pd.DataFrame:
    """
    Fetch SQL data.
    :param query: SQL query
    :return: dataframe with index set to UTCDateTime column,
        formatted as Timestamp
    """
    connector: SQLConnector = SQLConnector()
    data: pd.DataFrame = SQLConnector.exec_sql(connector, query)
    if "TimeStampUTC" in data:
        data.rename(columns={"TimeStampUTC": "UTCDateTime"}, inplace=True)
    data["UTCDateTime"] = pd.to_datetime(data["UTCDateTime"])
    return data.set_index("UTCDateTime").sort_index()


def get_power_data(building_name: str) -> pd.Series:
    """
    Retrieve and format power usage data.
    :param building_name: specific building name;
        capitalization insensitive
    :return: time series of power consumption
    """
    query: str = "SELECT * FROM "
    table: str = f"CEVAC_{building_name.upper()}_SPOWER_HIST"
    data: pd.DataFrame = get_sql(query + table)
    return data.rename(
        columns={"Value": "Power [kW]"}
    )["Power [kW]"]


def get_weather_data(mm_id: int) -> pd.Series:
    """
    Retrieve and format weather data.
    :param mm_id: 0 for cloud coverage, 6 for temperature
    :return: time series of weather data
    """
    historical: pd.DataFrame = get_sql(
        f"SELECT * FROM CEVAC_CAMPUS_WEATHER_HIST WHERE mm_id={mm_id}"
    )
    current_date: pd.Timestamp = historical.index[-1]

    forecast: pd.DataFrame = get_sql(
        f"SELECT * FROM CEVAC_CAMPUS_WEATHER_FORECAST_DAY WHERE mm_id={mm_id}"
    )
    forecast = forecast[forecast.index > current_date]

    rename = lambda table: table.rename(
        columns={
            "value": "Cloud Coverage [%]" if mm_id == 0 else "Temperature [C]"
        }
    )["Cloud Coverage [%]" if mm_id == 0 else "Temperature [C]"]

    historical, forecast = rename(historical), rename(forecast)

    return pd.concat([historical, forecast])


def get_occupancy_data(
        building_name: str,
        future_range: pd.Timedelta
) -> pd.Series:
    """
    Retrieve and format occupancy data.
    :param building_name: specific building name;
        capitalization insensitive
    :param future_range: range of future (predicted) data required
    :return: time series of occupancy data
    """
    query: str = "SELECT * FROM "
    table: str = f"CEVAC_{building_name.upper()}_WAP_FLOOR_SUMS_HIST"
    historical: pd.DataFrame = get_sql(query + table)
    current_date: pd.Timestamp = historical.index[-1]
    end_date: pd.Timestamp = current_date + future_range
    forecast: pd.Series = occupancy_forecast(
        current_date,
        end_date
    )
    historical = historical.rename(
        columns={"SUM_clemson_count": "Occupancy"}
    )["Occupancy"]
    return pd.concat([historical, forecast])


def occupancy_forecast(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
) -> pd.Series:
    """
    Retrieve Helena's occupancy forecast.
    :param start_date: start of forecast
    :param end_date: end of forecast
    :return: time series of occupancy forecast
    """
    # TODO: implement Helena's occupancy forecast
    return pd.Series(
        name="Occupancy",
        index=pd.date_range(
            start=start_date,
            end=end_date,
            freq="h",
            name="UTCDateTime"
        )
    )
