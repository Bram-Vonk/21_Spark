import logging
import math

import numpy as np
import pandas as pd

logger = logging.getLogger("SPARK")


def make_quantile_bands(df_base, samples, quantiles=(5, 15, 50, 85, 95)):
    """
    Translate samples to bands with edges defined by the given quantiles and merge them to a base dataFrame

    Parameters
    ----------
    df_base : pd.DataFrame
        base DataFrame with timestamps/length in accordance of the samples shape
    samples : np.array
        the posterior predictive samples
    quantiles: list
        an iterable with the edges of the bands (0,1), ordered increasingly.

    Returns
    -------
    pd.DataFrame
        long format version with the quantile bands of the samples
    """

    # get quantiles
    q_data = np.quantile(samples, [q / 100 for q in quantiles], axis=0)
    boundaries = ["upper", "lower"]
    df_bands = pd.DataFrame()

    # create bands from two quantile boundaries (median: upper=lower)
    for ci in range(math.ceil(len(quantiles) / 2)):
        # name band
        band_range = f"Q{quantiles[ci]}-Q{quantiles[-ci-1]}".replace(
            "Q50-Q50", "median"
        )

        df_band = df_base.copy()
        df_band[boundaries] = q_data[[-ci - 1, ci]].T
        df_band["band"] = band_range

        # append to other bands
        df_bands = pd.concat([df_bands, df_band], axis=0)

    # in long format
    df_bands = df_bands.melt(
        id_vars=df_bands.columns.difference(boundaries),
        value_vars=boundaries,
        var_name="boundary",
        value_name="value",
    )

    return df_bands


def format_model_estimates(df_base, pp, quantiles=(5, 15, 50, 85, 95)):
    """
    Format the samples into quantile bands for every model variable.

    Parameters
    ----------
    df_base : pd.DataFrame
        base DataFrame with timestamps/length in accordance of the samples shape
    pp : dict
        per model variable (key) the posterior predictive samples
    quantiles: list
        an iterable with the edges of the bands (0,1), ordered increasingly.

    Returns
    -------
    pd.DataFrame
        long format version with the quantile bands of the samples for every model variable

    """

    logger.info(f"calculating bands for quantiles: {quantiles}")
    df_vars = pd.DataFrame()
    for var, samples in pp.items():
        # get per model variable the quantile bands
        logger.info(f"calculating bands for variable: {var}")
        df_var = make_quantile_bands(
            df_base, samples=samples, quantiles=(5, 15, 50, 85, 95)
        ).assign(model_var=var)
        df_vars = pd.concat([df_vars, df_var], axis=0)

    return df_vars
