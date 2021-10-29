import datetime as dt
import logging
import os

import pandas as pd
import pymc3 as pm

from src.model.format import format_model_estimates
from src.model.model import create_model
from src.preprocess.preprocess import extrapolate_timestamps
from src.utils.parser import parse_config
from src.utils.preprocess import MinMaxScaler
from src.preprocess.preprocess import load_data

logger = logging.getLogger("SPARK")

config = parse_config(
    os.path.abspath(
        os.path.join(os.path.join(os.path.dirname(__file__), "../settings.yml"))
    )
)


def determine_estimates(df_observed):
    """
    Determine model parameters and forecast for a extreme (max or min).

    Parameters
    ----------
    df_observed : pd.DataFrame
        observed values of DALI data

    Returns
    -------
    pd.DataFrame
        estimates for extreme
    """
    # extend date
    logger.info(f"add forecast horizon")
    df_future = extrapolate_timestamps(
        df_observed, horizon=dt.timedelta(weeks=config["model"]["fc_horizon"])
    )
    df_full_range = pd.concat([df_observed, df_future])

    logger.info(f"scale data")
    # scale t, y, p
    t_scaler = MinMaxScaler(lower=0)
    t = t_scaler.fit_transform(X=df_full_range["date"])
    y_scaler = MinMaxScaler(lower=0)
    y_observed = y_scaler.fit_transform(X=df_full_range["value"])
    # y_observed = np.ma.masked_invalid(y_observed)
    p = t_scaler.transform(t_scaler.min + dt.timedelta(weeks=52.1775))

    # create model
    logger.info(f"setup model")
    m = create_model(
        t=t,
        y=y_observed,
        p_fourier=p,
        n_fourier=config["model"]["n_fourier"],
        n_polynomial=config["model"]["n_polynomial"],
    )

    # display(pm.model_to_graphviz(m))
    logger.info(f"tune and sample model")
    # tune model
    trace = pm.sample(
        model=m,
        draws=config["model"]["draws"],
        tune=config["model"]["tune"],
        init="adapt_diag",
    )
    # extract posterior predictions
    pp = pm.sample_posterior_predictive(
        model=m,
        trace=trace,
        samples=config["model"]["tune"],
        var_names=["drift", "yearly", "Σ"],
    )

    logger.info(f"scale ouput data back")
    # inverse scale samples
    for k in pp.keys():
        pp[k] = y_scaler.inverse_transform(pp[k])
        if k == "yearly":
            pp[k] -= y_scaler.min

    logger.info(f"format output data")
    # create base df and join it with posterior predictive quantiles
    df_base = df_full_range.drop(columns=["value", "processed_on", "model_var"]).copy()
    df_estimates = format_model_estimates(
        df_base, pp, quantiles=config["model"]["quantiles"]
    )

    return df_estimates


def determine_estimates_minmax(df_observed):
    """
    Determine model parameters and forecast for a extreme (max or min).

    Parameters
    ----------
    df_observed : pd.DataFrame
        observed values of DALI data

    Returns
    -------
    pd.DataFrame
        estimates for min and max
    """
    df_estimates = pd.DataFrame()
    for extreme in ["min", "max"]:
        logger.info(f"forecast for weekly {extreme}")
        df_extreme = determine_estimates(df_observed.query(f"extreme == '{extreme}'"))
        df_estimates = pd.concat([df_estimates, df_extreme], axis=0)
    return df_estimates


def forecast(boxid=None):
    """
    Forecast for one or more DALI boxes.

    Parameters
    ----------
    boxid : list
        string or list with boxids to forecast for.

    Returns
    -------
    pd.DataFrame
        DataFrame with observations and forecast on long format
    """
    if isinstance(boxid, (str)):
        boxid = [boxid]

    df_total = pd.DataFrame()
    for box in boxid:
        result = load_data(boxid=box)
        if result is not None:
            logger.info(f"Forecasting boxid: {box}")
            df_data, df_meta = result
            df_estimates = determine_estimates_minmax(df_data)
            df_total = pd.concat([df_total, df_data, df_estimates], axis=0)
        else:
            logger.info(f"Can not forecast boxid: {box}")
    return df_total
