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


def split_last(df_data, period=dt.timedelta(weeks=26)):
    split = df_data["date"].max() - period
    df_train = df_data[df_data["date"] < split]
    df_test = df_data[df_data["date"] >= split]
    return df_train, df_test
