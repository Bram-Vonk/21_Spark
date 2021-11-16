import pandas as pd
import logging

logger = logging.getLogger("SPARK")

def asses_forecasts(df_total, df_meta):
    logger.info(f"Assessing forecast")

    # get maximum of forecast
    df_assess = df_total.query("period == 'future' & model_var == 'Σ'").copy()
    df_assess["relative_abs_max"] = (df_assess["value"].abs() / df_meta["vermogen_nominaal"].squeeze()
    ).clip(upper=1)
    df_assess["date_abs_max"] = df_assess["date"]
    df_assess = df_assess.sort_values(by=["relative_abs_max", "date_abs_max"], ascending=[False, True]).iloc[[0]]

    df_forecast_meta = pd.merge(df_meta, df_assess, on="boxid")
    df_forecast_meta["regio"] = df_forecast_meta["regio_netautomatisering"]
    cols = [
        "boxid",
        "stationsnummer",
        "regio",
        "vestiging",
        "l",
        "processed_on",
        "vermogen_nominaal",
        "relative_abs_max",
        "date_abs_max",
    ]

    return df_forecast_meta[cols]