import pandas as pd
from CEVAC.Connectors import SQLConnector
from occupancy_forecasting import Predictor
from power_forecasting.buildings import Building


def load_all_data(
        building: Building,
        start_date: pd.Timestamp,
        future_range: pd.Timedelta,
        history_range: pd.Timedelta
) -> (pd.DataFrame, pd.DataFrame):
    if future_range is None:
        future_range = pd.Timedelta(days=1)

    if history_range is None:
        history_range = pd.Timedelta(weeks=2)

    power_data: pd.Series = power(building)

    if start_date is None:
        start_date = power_data.index[-1] + pd.Timedelta(hours=1)

    power_data = power_data.reindex(pd.date_range(
        start_date - history_range,
        start_date - pd.Timedelta(hours=1),
        freq="h",
        name=power_data.index.name
    ))

    historical = load_regressors(
        start_date - history_range,
        start_date - pd.Timedelta(hours=1),
        building
    )
    historical = pd.concat([power_data, historical], axis=1)

    future = load_regressors(
        start_date,
        start_date + future_range - pd.Timedelta(hours=1),
        building
    )

    return historical, future


def load_regressors(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        building: Building
) -> pd.DataFrame:
    """Load variables in given range, stored as DateTime indexed DataFrame.
    Current variables include:
        - Temperature [C]
        - Cloud Coverage [%]
        - Occupancy

    :param start_date:
    :param end_date:
    :param building_name:
    :return:
    """
    return pd.concat(
        objs=[
            temperature(start_date, end_date),
            clouds(start_date, end_date),
            occupancy(start_date, end_date, building),
        ],
        axis=1
    )


def power(building: Building) -> pd.Series:
    query = "SELECT * FROM "
    table = f"CEVAC_{building.name.upper()}_SPOWER_HIST"
    power_data = group_by_hour(get_sql(query + table, "Value", "Power [kW]"))

    return power_data


def temperature(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
) -> pd.Series:
    return weather(
        start_date,
        end_date,
        "Temperature [C]",
        0
    )


def clouds(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
) -> pd.Series:
    return weather(
        start_date,
        end_date,
        "Cloud Coverage [%]",
        6
    )


def occupancy(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        building: Building
) -> pd.Series:
    query = "SELECT * FROM "
    table = f"CEVAC_{building.name.upper()}_WAP_FLOOR_SUMS_HIST"
    historical = get_sql(
        query + table,
        "SUM_clemson_count",
        "Occupancy"
    )

    predictor = Predictor(
        building=building.occupancy_building
    )
    # TODO: integrate with Helena's model
    future = predictor.forecast(start_date, end_date)

    occupancy_data = pd.concat([historical, future])
    occupancy_data = group_by_hour(occupancy_data)
    occupancy_data = occupancy_data.reindex(pd.date_range(
        start_date,
        end_date,
        freq="h",
        name=occupancy_data.index.name
    ))
    return occupancy_data


def weather(
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
        name: str,
        mm_id: int
) -> pd.Series:
    historical = get_sql(
        f"SELECT * FROM CEVAC_CAMPUS_WEATHER_HIST WHERE mm_id={mm_id}",
        "value",
        name
    )
    future = get_sql(
        f"SELECT * FROM CEVAC_CAMPUS_WEATHER_FORECAST_DAY WHERE mm_id={mm_id}",
        "value",
        name
    )
    weather_data = pd.concat([historical, future])
    weather_data = group_by_hour(weather_data)
    weather_data = weather_data.reindex(pd.date_range(
        start=start_date,
        end=end_date,
        freq="h",
        name=weather_data.index.name
    ))
    return weather_data


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
