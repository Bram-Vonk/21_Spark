import datetime as dt

import pandas as pd


def format_limits(df_meta, df_data=None):
    limit = df_meta["vermogen_nominaal"].squeeze()

    if df_data is None:
        return pd.DataFrame({"limit": ["lower", "upper"], "value": [-limit, limit]})
    else:
        df_plot = df_data.sort_values(["date"]).iloc[[1, -1]][["date"]]
        df_plot["lower"] = -limit
        df_plot["upper"] = limit
        return df_plot.melt(id_vars=["date"], value_vars=["lower", "upper"], var_name=["limit"])


def format_history(df_data):
    df_plot = df_data.copy()
    value_vars = ["min", "max"]
    df_plot = df_plot.melt(
        var_name="history",
        value_name="power",
        id_vars=df_plot.columns.difference(value_vars),
        value_vars=value_vars,
    )
    return df_plot


def format_forecast(df):
    return df


def split_last(df_data, period=dt.timedelta(weeks=26)):
    split = df_data["date"].max() - period
    df_train = df_data[df_data["date"] < split]
    df_test = df_data[df_data["date"] >= split]
    return df_train, df_test


def dummy_forecast(df):
    extremes = ["max", "min"]
    df = df.melt(
        id_vars=df.columns.difference(extremes),
        value_vars=extremes,
        var_name="extreme",
    )
    df["forecast"] = "Q10-Q90"
    df["upper"] = df["value"]+50
    df["lower"] = df["value"]-50

    df_median = df.copy()
    df_median["forecast"] = "median"
    df_median["upper"] = df_median["value"]
    df_median["lower"] = df_median["value"]
    df_forecast = pd.concat([df, df_median])
    return df_forecast