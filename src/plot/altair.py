import altair as alt

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
                y=alt.Y("value:Q", title=""),
                color=alt.Color("transformer:N", scale=alt.Scale(range=["red"])),
            )
                .properties(width=800)
        ).interactive()
    else:
        return (
            alt.Chart(df_limits)
                .mark_rule(strokeDash=[5, 5])
                .encode(
                y=alt.Y("value:Q", title=""),
                color=alt.Color(
                    "transformer:N", title="", scale=alt.Scale(range=["red"])
                ),
            )
                .properties(width=800)
        ).interactive()
