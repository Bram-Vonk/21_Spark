import datetime as dt

import pandas as pd


def format_limits(df_meta, df_data=None):
    """
    Format the transformer limits for plotting.

    Parameters
    ----------
    df_meta: pd.DataFrame
        DataFrame with the trasnformer limits.
    df_data: pd.DataFrame
        Optionally, the historic data to determine the time range for the limits.

    Returns
    -------
        A DataFrame with the limits to plot.
    """
    limit = df_meta["vermogen_nominaal"].squeeze()

    if df_data is None:
        return pd.DataFrame({"limit": ["lower", "upper"], "value": [-limit, limit]})
    else:
        df_plot = df_data.sort_values(["date"]).iloc[[1, -1]][["date"]]
        df_plot["lower"] = -limit
        df_plot["upper"] = limit
        return df_plot.melt(
            id_vars=["date"], value_vars=["lower", "upper"], var_name=["limit"]
        )


def format_history(df_data):
    """
    Format the historic for plotting.

    Parameters
    ----------
    df_data: pd.DataFrame
        The historic data to be plotted.

    Returns
    -------
        A DataFrame with the historic data to plot.
    """
    df_plot = df_data.copy()
    value_vars = ["min", "max"]
    df_plot = df_plot.melt(
        var_name="history",
        value_name="power",
        id_vars=df_plot.columns.difference(value_vars),
        value_vars=value_vars,
    )
    return df_plot


def format_forecast(df_forecast):
    """
    Format the forecasted load.

    Parameters
    ----------
    df: pd.DataFrame

    Returns
    -------
        pass through input
    """
    return df_forecast


def split_last(df_data, period=dt.timedelta(weeks=26)):
    """
    Split the historic dataset into a train and test set a certain period from the end.

    Parameters
    ----------
    df_data: pd.DataFrame
        Dataset to split.
    period: datetime
        Period from the end to split from
    Returns
    -------
        df_train, df_test

    """
    split = df_data["date"].max() - period
    df_train = df_data[df_data["date"] < split]
    df_test = df_data[df_data["date"] >= split]
    return df_train, df_test


def dummy_forecast(df):
    """
    Create a dummy forecast with median and Q10-Q90 based on historic data to test plotting function.

    Parameters
    ----------
    df : pd.DataFrame
        Historic data to use as a basis

    Returns
    -------
    pd.DataFrame
        Forecast data that can be used to plot with plot_forecast()

    """
    extremes = ["max", "min"]
    df = df.melt(
        id_vars=df.columns.difference(extremes),
        value_vars=extremes,
        var_name="extreme",
    )
    df["forecast"] = "Q10-Q90"
    df["upper"] = df["value"] + 50
    df["lower"] = df["value"] - 50

    df_median = df.copy()
    df_median["forecast"] = "median"
    df_median["upper"] = df_median["value"]
    df_median["lower"] = df_median["value"]
    df_forecast = pd.concat([df, df_median])
    return df_forecast
