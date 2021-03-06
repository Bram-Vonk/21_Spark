#  Copyright (c) 2021. Bram Vonk, Enexis

import logging

from src.forecast.forecast import forecast
from src.utils.snowflake import (
    clear_forecasts,
    get_forecasted_boxids,
    read_meta,
    write_forecast_meta,
    write_forecasts,
)

logger = logging.getLogger("SPARK")


def make_forecasts(clear=False):
    """
    Make forecasts for all boxes.

    Parameters
    ----------
    clear: bool
        Clear the Snowflake table

    Returns
    -------
    None
    """
    if clear:
        clear_forecasts()

    # boxids = ['HLD.301001-1', 'MRS.HEKST-1', 'DVT.141032-1', 'LSM.270004-1',
    #           '133.938-1', 'ESD.000047-1', 'DVT.141236-1', 'WRT.CELSW-1',
    #           '121.544-1', 'DVT.141063-1']
    boxids = list(read_meta()["boxid"].unique())
    boxids = set(boxids) - set(list(get_forecasted_boxids()["boxid"]))

    for i, boxid in enumerate(list(boxids)):

        logger.info(f"Forecasting boxid # {i+1} / {len(boxids)}")

        df_total, df_forecast_meta = forecast(boxid=boxid)
        if len(df_total):
            write_forecasts(df_total)
            write_forecast_meta(df_forecast_meta)


if __name__ == "__main__":
    make_forecasts()
