import re
import colour
import numpy as np
import altair as alt

from src.plot.formatting import format_forecast, format_history, format_limits

alt.data_transformers.disable_max_rows()


def plot_estimate(df, legend=True):
    """
    Plot the load forecast transformer.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the columns date, lower, upper, forecast(Q10-Q190, median), extreme

    Returns
    -------
        Altair chart
    """
    if legend:
        legend=dict()
    else:
        legend=dict(legend=None)
    # to solve: using longformat for y and y2, till then reformat boundaries
    df = (
        df.pivot(
            index=df.columns.difference(["boundary", "value"]),
            columns="boundary",
            values="value",
        )
        .reset_index()
        .rename_axis(columns=None)
    )

    # get ranges and coloring correct
    ranges = [r for r in df["band"].unique() if r is not np.nan]
    ranges.sort(key=lambda item: (len(item), item))
    if "median" in ranges:
        ranges.remove("median")
        ranges.append("median")
    ranges = ranges[::-1]
    parsed = [re.match("^Q(\d{1,2})-", s) for s in ranges]
    factors = [1 if res is None else (2 * int(res.groups()[0]) / 100) for res in parsed]
    colors = [lightness_scale(f) for f in factors]

    return (
        alt.Chart(df)
        .mark_area(line=True)
        .encode(
            x=alt.X("date:T", title="data"),
            y=alt.Y("lower:Q", stack=None, title="power [kW]"),
            y2=alt.Y2("upper:Q", title=""),
            color=alt.Color(
                "band:N",
                title="estimate",
                scale=alt.Scale(domain=ranges, range=colors),
                **legend,
            ),
            detail="extreme:N",
        )
        .properties(width=800)
        #.interactive()
    )


def plot_observed(df):
    """
    Plot the historic/observed load of a transformer.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with like:

    Returns
    -------
        Altair chart
    """
    alt_history = (
        alt.Chart(df.query("model_var == 'observed'"))
        .mark_point(color="black")
        .encode(
            x=alt.X("date:T", title="date"),
            y=alt.Y("value:Q", title="power [kW]"),
            shape=alt.Shape(
                "extreme:N", title="history",
                scale=alt.Scale(
                    domain=["max", "min"],
                    range=["triangle-up", "triangle-down"],
                ),
            ),
            tooltip=[
                alt.Tooltip("value:Q", title="power", format=".2f"),
                alt.Tooltip("extreme:N"),
                alt.Tooltip("year:Q"),
                alt.Tooltip("week:Q"),
            ],
        )
        .properties(width=800)
    ).interactive()
    return alt_history


def plot_limits(df):
    """
    Plot the capacity limits of a transformer as a ruler of as a line if metadata changes over time.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the limits to be plotted

    Returns
    -------
        Altair chart
    """
    df["transformer"] = "capacity"
    if "date" in df.columns:
        return (
            alt.Chart(df)
            .mark_line(strokeDash=[5, 5])
            .encode(
                x=alt.X("date:T", title="date"),
                y=alt.Y("value:Q", title="power [kW]"),
                color=alt.Color("transformer:N", scale=alt.Scale(range=["red"])),
                detail=("limit:N"),
            )
            .properties(width=800)
        )#.interactive()
    else:
        return (
            alt.Chart(df)
            .mark_rule(strokeDash=[5, 5])
            .encode(
                y=alt.Y("value:Q", title="power [kW]"),
                color=alt.Color("transformer:N", scale=alt.Scale(range=["red"])),
            )
            .properties(width=800)
        )#.interactive()


def lightness_scale(factor, limits=["#bedef4", "#1f77b4"]):
    h0 = colour.hex2hsl(limits[0])
    h1 = colour.hex2hsl(limits[1])
    color = [(1-factor)*v0 + factor*v1 for v0,v1 in zip(h0, h1)]
    return colour.hsl2hex(color)


def plot_forecast(df):
    """
    Plot the load forecast transformer.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the columns date, lower, upper, forecast(Q10-Q190, median), extreme

    Returns
    -------
        Altair chart
    """

    ranges = list(df["forecast"].unique())
    ranges.sort(key=lambda item: (len(item), item))
    if "median" in ranges:
        ranges.remove("median")
        ranges.append("median")
    ranges = ranges[::-1]
    parsed = [re.match("^Q(\d{1,2})-", s) for s in ranges]
    factors = [1 if res is None else (2 * int(res.groups()[0]) / 100) for res in parsed]
    colors = [lightness_scale(f) for f in factors]
    return (
        alt.Chart(df)
        .mark_area(line=True)
        .encode(
            x=alt.X("date:T", title="date"),
            y=alt.Y("lower:Q", stack=None, title="power [kW]"),
            y2=alt.Y2("upper:Q", title=""),
            color=alt.Color(
                "forecast:N",
                scale=alt.Scale(domain=ranges, range=colors),
            ),
            detail="extreme:N",
        )
        .properties(width=800)
        .interactive()
    )

def plot_total(df_data=None, df_meta=None):
    """
    Plot one or more of the following: history, forecast, transformer limits.

    Parameters
    ----------
    df_data : pd.DataFrame
        DataFrame with the timeseries
    df_meta : pd.DataFrame
        DataFrame with the metadata

    Returns
    -------
        Altair layer chart
    """
    plots = []

    if df_data is not None:
        df_estimates = df_data.query("model_var!='observed'").dropna(subset=["model_var"])
        if len(df_estimates):
            plots.append(plot_estimate(df_estimates))

        df_observed = df_data.query("model_var=='observed'")
        if len(df_observed):
            plots.append(plot_observed(df_observed))

    if df_meta is not None:
        limits_plot = plot_limits(format_limits(df_meta=df_meta, df_data=None))
        plots.append(limits_plot)

    return (
        alt.layer(*plots)
        .resolve_scale(color="independent", shape="independent")
        # .interactive()
    )


# def plot_total(df_data=None, df_meta=None, df_forecast=None):
#     """
#     Plot one or more of the following: history, forecast, transformer limits.
#
#     Parameters
#     ----------
#     df_data : pd.DataFrame
#         DataFrame with the historic preprocess
#     df_meta : pd.DataFrame
#         DataFrame with the metadata
#     df_forecast : pd.DataFrame
#         DataFrame with forecasts
#
#     Returns
#     -------
#         Altair layer chart
#     """
#     plots = []
#
#     if df_forecast is not None:
#         forecast_plot = plot_forecast(format_forecast(df_forecast))
#         plots.append(forecast_plot)
#
#     if df_data is not None:
#         history_plot = plot_history(format_history(df_data))
#         plots.append(history_plot)
#
#     if df_meta is not None:
#         limits_plot = plot_limits(format_limits(df_meta=df_meta, df_data=None))
#         plots.append(limits_plot)
#
#     return (
#         alt.layer(*plots)
#         .resolve_scale(color="independent", shape="independent")
#         .interactive()
#     )
