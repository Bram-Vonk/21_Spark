import pandas as pd
import datetime as dt

def format_limits(df_meta, df_data=None):
    limit = df_meta["vermogen_nominaal"].squeeze()

    if df_data is None:
        return pd.DataFrame({"limit": ["lower", "upper"], "value": [-limit, limit]})
    else:
        timestamps = [df_data["date"].min(), df_data["date"].max()]

        return pd.DataFrame(
            {
                "date": timestamps,
                "lower": [-limit] * len(timestamps),
                "upper": [limit] * len(timestamps),
            }
        ).melt(id_vars=["date"], value_vars=["lower", "upper"], var_name=["limit"])


def format_history(df_data):
    df_plot = df_data.copy()
    df_plot["date"] = df_plot.apply(lambda df: dt.datetime.fromisocalendar(df["year"], df["week"], 1), axis=1)
    value_vars = ["min", "max"]
    df_plot = df_plot.melt(
        var_name="history",
        value_name="power",
        id_vars=df_plot.columns.difference(value_vars),
        value_vars=value_vars,
    )
    return df_plot
