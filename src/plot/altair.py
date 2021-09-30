import altair as alt
from src.plot.formatting import format_limits, format_history, format_forecast

alt.data_transformers.disable_max_rows()


def plot_history(df):
    alt_history = (
        alt.Chart(df)
            .mark_point(color="black")
            .encode(
            x=alt.X("date:T", title="date"),
            y=alt.Y("power:Q", title="power [kW]"),
            shape=alt.Shape(
                "history",
                scale=alt.Scale(
                    domain=["max", "min"],
                    range=["triangle-up", "triangle-down"],
                ),
            ),
            tooltip=[
                alt.Tooltip("power:Q", format=".2f"),
                alt.Tooltip("history:N"),
                alt.Tooltip("year:Q"),
                alt.Tooltip("week:Q"),
            ],
        )
            .properties(width=800)
    ).interactive()
    return alt_history


def plot_limits(df_limits):
    df_limits["transformer"] = "capacity"
    if "date" in df_limits.columns:
        return (
            alt.Chart(df_limits)
                .mark_line(strokeDash=[5, 5])
                .encode(
                x=alt.X("date:T", title="date"),
                y=alt.Y("value:Q", title="power [kW]"),
                color=alt.Color("transformer:N", scale=alt.Scale(range=["red"])),
                detail=("limit:N"),
            )
                .properties(width=800)
        ).interactive()
    else:
        return (
            alt.Chart(df_limits)
                .mark_rule(strokeDash=[5, 5])
                .encode(
                y=alt.Y("value:Q", title="power [kW]"),
                color=alt.Color(
                    "transformer:N", scale=alt.Scale(range=["red"])
                ),
            )
                .properties(width=800)
        ).interactive()


def plot_forecast(df_forecast):

    return alt.Chart(df_forecast).mark_area(line=True).encode(
        x=alt.X("date:T"),
        y=alt.Y("lower:Q", stack=None, title=""),
        y2=alt.Y2("upper:Q", title=""),
        opacity=alt.Opacity("forecast:N", scale=alt.Scale(domain=["Q10-Q90", "median"], range=[.3, 1])),
        detail="extreme:N"
    ).interactive()


def plot_total(df_data=None, df_meta=None, df_forecast=None):
    plots = []

    if df_forecast is not None:
        forecast_plot = plot_forecast(format_forecast(df_forecast))
        plots.append(forecast_plot)

    if df_data is not None:
        history_plot = plot_history(format_history(df_data))
        plots.append(history_plot)

    if df_meta is not None:
        limits_plot = plot_limits(format_limits(df_meta=df_meta, df_data=None))
        plots.append(limits_plot)

    return (
        alt.layer(*plots)
        .resolve_scale(color="independent", shape="independent")
        .interactive()
    )