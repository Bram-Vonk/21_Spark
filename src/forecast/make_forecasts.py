from src.utils.snowflake import read_meta, clear_forecasts, write_forecasts
from src.forecast.forecast import forecast


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

    boxids = ['HLD.301001-1', 'MRS.HEKST-1', 'DVT.141032-1', 'LSM.270004-1',
              '133.938-1', 'ESD.000047-1', 'DVT.141236-1', 'WRT.CELSW-1',
              '121.544-1', 'DVT.141063-1']
    # boxids = read_meta()["boxid"].unique()

    for boxid in boxids:
        df_total = forecast(boxid=boxid)
        if len(df_total):
            write_forecasts(df_total)


if __name__ == "__main__":
    make_forecasts()
