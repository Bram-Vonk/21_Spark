#  Copyright (c) 2021. Bram Vonk, Enexis

import pandas as pd
import panel as pn

from src.plot.altair import plot_all, plot_decompose
from src.utils.snowflake import read_forecast_meta, read_forecasts

# alt.renderers.enable("default")
# pn.extension("vega")
pn.extension("tabulator")


def build_dashboard_():
    """
    Initialize dashboard.

    Returns
    -------
    None
    """
    # read and format forecasts metadata / assessment
    df_forecast_meta = read_forecast_meta()
    df_table = df_forecast_meta.rename(
        columns={
            "vermogen_nominaal": "P_nom",
            "relative_abs_max": "P_max",
            "date_abs_max": "t_max",
        }
    )[["boxid", "P_max", "t_max", "vestiging"]].sort_values(by=["P_max", "t_max"], ascending=[False, True])
    df_table["t_max"] = pd.to_datetime(df_table["t_max"]).dt.date

    # configure tabulator for prioritization list of transformers
    tabulator_formatters = {
        "P_max": {
            "type": "progress",
            "max": 1,
            "color": ["green"] * 80 + ["orange"] * 15 + ["red"] * 5,
        },
    }

    table = pn.widgets.Tabulator(
        df_table.copy(),
        formatters=tabulator_formatters,
        show_index=False,
        disabled=True,
        selectable=1,
        height=500,
        width=400,
        selection=[0],
        width_policy="min",
    )

    # enable filter on sub-service area
    vestigingen = list(df_table["vestiging"].unique())
    choice_vestiging = pn.widgets.CheckButtonGroup(
        name="regio",
        value=vestigingen,
        options=vestigingen,
        width=1100,
    )

    table.add_filter(choice_vestiging, "vestiging")

    # update tabs callback
    def update_tabs(selection):
        # extract boxid
        boxid = table.value["boxid"].iloc[selection].squeeze()

        df_total = read_forecasts(boxid=boxid)

        plot_total = plot_all(
            df_data=df_total,
            df_meta=df_forecast_meta[df_forecast_meta["boxid"] == boxid],
        ).properties(width=600, height=400)

        plot_min = plot_decompose(df_total[df_total["extreme"] == "min"])

        plot_max = plot_decompose(df_total[df_total["extreme"] == "max"])

        return pn.Tabs(
            ("general", plot_total),
            ("breakdown min", plot_min),
            ("breakdown max", plot_max),
            width_policy="max",
        )

    tabs = pn.bind(update_tabs, selection=table.param.selection)

    # define panel
    panel = pn.Column(choice_vestiging, pn.Row(table, tabs, min_height=500))

    # pn.serve(panel)
    # panel.servable()

    return panel


def build_dashboard():
    return pn.pane.Markdown("Hello World")

if __name__.startswith("bokeh"):
    # start with panel serve script.py
    dashboard = build_dashboard()
    dashboard.servable()
if __name__ == "__main__":
    # start with python script.py
    dashboard = build_dashboard()
    dashboard.show(port=5007)