import pandas as pd
from CEVAC.Connectors import SQLConnector
from occupancy_forecasting import Predictor
from power_forecasting.buildings import Building


# TODO: get future range in here somehow
def load_future_data(
        building: Building,
        future_range: pd.Timedelta
) -> pd.DataFrame:
    """Get forecast data

    :param building:
    :param future_range:
    :return:
    """
    temperature: pd.Series = group_by_hour(future_weather_data(0))
    clouds: pd.Series = group_by_hour(future_weather_data(6))
    occupancy: pd.Series = group_by_hour(future_occupancy_data(
        building,
        future_range
    ))
    data: pd.DataFrame = pd.concat(
        [temperature, clouds, occupancy],
        axis=1
    )
    data.name = building.name
    data = reindex(data)

    return data


def future_weather_data(mm_id: int) -> pd.Series:
    """Retrieve and format weather forecasts.

    :param mm_id: 0 for cloud coverage, 6 for temperature
    :return: time series of weather forecast
    """
    data: pd.Series = get_sql(
        f"SELECT * FROM CEVAC_CAMPUS_WEATHER_FORECAST_DAY WHERE mm_id={mm_id}",
        "value",
        "Cloud Coverage [%]" if mm_id == 0 else "Temperature [C]"
    )

    return data


# TODO: integrate this with Helena's model
def future_occupancy_data(
        building: Building,
        future_range: pd.Timedelta
) -> pd.Series:
    """Retrieve and format occupancy forecasts from Helena's model.

    :param building:
    :param future_range:
    :return:
    """
    predictor: Predictor = Predictor(
        building=building.occupancy_building
    )
    return predictor.forecast(future_range)


def load_historical_data(
        building: Building
) -> pd.DataFrame:
    """
    Read from SQL Server, and compile everything into one dataframe.
    :param building: specific building name;
        capitalization insensitive
    :param future_range:
    :return: compiled dataframe
    """
    power: pd.Series = group_by_hour(historical_power_data(building.name))
    clouds: pd.Series = group_by_hour(historical_weather_data(0))
    temperature: pd.Series = group_by_hour(historical_weather_data(6))
    occupancy: pd.Series = group_by_hour(
        historical_occupancy_data(building)
    )
    data: pd.DataFrame = pd.concat(
        [power, temperature, clouds, occupancy],
        axis=1
    )
    data.name = building.name
    data = reindex(data)

    return data


def group_by_hour(data: pd.Series) -> pd.Series:
    """
    Take a time series and produce hourly means.
    This helps "line up" real world data where observations are mismatched.
    :param data: time series, whose index is "UTCDateTime"
    :return: hourly time series
    """
    group: pd.DataFrame = data.groupby(
        [data.index.date, data.index.hour]
    ).mean().reset_index()
    group["level_0"] = pd.to_datetime(group["level_0"])
    group["UTCDateTime"] = pd.to_timedelta(group["UTCDateTime"], unit="h")
    group["UTCDateTime"] += group["level_0"]
    return group.set_index("UTCDateTime")[data.name]


def get_sql(query: str, column: str, rename: str) -> pd.Series:
    """
    Fetch SQL data.
    :param query: SQL query
    :param column: column of the dataframe to read
    :param rename: string to rename desired column
    :return: series with index set to UTCDateTime column,
        formatted as Timestamp
    """
    connector: SQLConnector = SQLConnector()
    data: pd.DataFrame = SQLConnector.exec_sql(connector, query)
    if "TimeStampUTC" in data:
        data.rename(columns={"TimeStampUTC": "UTCDateTime"}, inplace=True)
    data["UTCDateTime"] = pd.to_datetime(data["UTCDateTime"])
    data.set_index("UTCDateTime", inplace=True)
    data.rename(columns={column: rename}, inplace=True)
    return data[rename]


def historical_power_data(building_name: str) -> pd.Series:
    """
    Retrieve and format power usage data.
    :param building_name: specific building name;
        capitalization insensitive
    :return: time series of power consumption
    """
    query: str = "SELECT * FROM "
    table: str = f"CEVAC_{building_name.upper()}_SPOWER_HIST"
    return get_sql(query + table, "Value", "Power [kW]")


def historical_weather_data(mm_id: int) -> pd.Series:
    """
    Retrieve and format weather data.
    :param mm_id: 0 for cloud coverage, 6 for temperature
    :return: time series of weather data
    """
    data: pd.Series = get_sql(
        f"SELECT * FROM CEVAC_CAMPUS_WEATHER_HIST WHERE mm_id={mm_id}",
        "value",
        "Cloud Coverage [%]" if mm_id == 0 else "Temperature [C]"
    )

    return data


# TODO: fix this and other docstrings
def historical_occupancy_data(building: Building) -> pd.Series:
    """
    Retrieve and format occupancy data.
    :param building: specific building name;
        capitalization insensitive
    :return: time series of occupancy data
    """
    query: str = "SELECT * FROM "
    table: str = f"CEVAC_{building.name.upper()}_WAP_FLOOR_SUMS_HIST"
    data: pd.Series = get_sql(
        query + table,
        "SUM_clemson_count",
        "Occupancy"
    )
    return data


def reindex(data: pd.DataFrame) -> pd.DataFrame:
    """
    Insert rows of missing data wherever index is inconsistent.
    :param data: data frame with inconsistent index
    :return: data frame with rows of missing data
    """
    data = data.reindex(pd.date_range(
        data.index[0],
        data.index[-1],
        freq="h",
        name=data.index.name
    ))

    return data
