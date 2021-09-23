import altair as alt

alt.data_transformers.disable_max_rows()


def plot_observed(df):

    alt_observed = (
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
    return alt_observed
