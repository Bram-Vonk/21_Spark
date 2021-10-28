import logging

import numpy as np
import pymc3 as pm

logger = logging.getLogger("SPARK")


def det_dot(a, b):
    """
    Dot product for Theano.

    The theano dot product and NUTS sampler don't work with large matrices.
    source: https://www.ritchievink.com/blog/2018/10/09/ ...
    build-facebooks-prophet-in-pymc3-bayesian-time-series-analyis-with-generalized-additive-models/

    Parameters
    ----------
    a : np.array
    b : tt.vector

    Returns
    -------
    np.array
        dot product of the two.

    """
    return (a * b[None, :]).sum(axis=-1)


def fourier_series(t, p=52.1775, n=5):
    """
    Calculate fourier representation of t for a period and order.

    Based on source: https://www.ritchievink.com/blog/2018/10/09/ ...
    build-facebooks-prophet-in-pymc3-bayesian-time-series-analyis-with-generalized-additive-models/

    Parameters
    ----------
    t : range
        range to be used as input variable
    p : float
        period to use for the fourier orders
    n : int
        order of fourier series

    Returns
    -------
    np.array
        matrix fourier representation of t

    """
    # 2 pi n / p * t
    x = 2 * np.pi * np.arange(1, n + 1) / p
    x = x * t[:, None]
    x = np.concatenate((np.cos(x), np.sin(x)), axis=1)
    return x


def seasonality_model(t, p=52.1775, n=5, seasonality_prior_scale=1):
    """
    Create seasonality model with fourier series.

    Based on source: https://www.ritchievink.com/blog/2018/10/09/ ...
    build-facebooks-prophet-in-pymc3-bayesian-time-series-analyis-with-generalized-additive-models/

    Parameters
    ----------
    t : range
        range to be used as input variable
    p : float
        period to use for the fourier orders
    n : int
        order of fourier series
    seasonality_prior_scale: float

    Returns
    -------
    pm.var
        PYMC3 variable

    """
    x = fourier_series(t, p=p, n=n)
    β = pm.Normal("β_yearly", mu=0, sd=seasonality_prior_scale, shape=2 * n)
    return pm.Deterministic("yearly", det_dot(x, β))


def polynomial(t, n=4):
    """
    Calculate polynomial representation of t for an order.

    Parameters
    ----------
    t : range
        range to be used as input variable
    n : int
        order of polynomial

    Returns
    -------
    np.array
        matrix polynomial representation of t

    """
    p = np.arange(n + 1)
    x = np.power(t[:, None], p)
    return x


def drift_model(t, n=4):
    """
    Polynomal drift/trend function for additive model.

    Parameters
    ----------
    t : range
        range to be used as input variable
    n : int
        order of polynomal.

    Returns
    -------
    pm.var
        PYMC3 variable

    """
    x = polynomial(t, n=n)
    β = pm.Normal("β_drift", mu=0, sd=0.5, shape=n + 1)

    return pm.Deterministic("drift", det_dot(x, β))


def create_model(t, y, p_fourier, n_fourier=5, n_polynomial=2):
    """
    Create a PYMC3 GAM model with a trend/drift and a seasonal/yearly component.

    Parameters
    ----------
    t : timestamps
        input series of scaled timestamps
    y : float
        observed values
    p_fourier: float
        scaled period of the timestamps to take for the fourier component (a year)
    n_fourier : int
        order of the fourier component
    n_polynomial: inbt
        order of the polynomial component

    Returns
    -------
    PYMC3 model context
    """

    logger.info(f"creating PYMC3 model")
    logger.info(f"polynomial order = {n_polynomial} for drift/trend")
    logger.info(f"fourier order = {n_fourier} for seasonality")
    with pm.Model() as m:
        drift = drift_model(t, n=n_polynomial)
        yearly = seasonality_model(t, p=p_fourier, n=n_fourier)

        σ_ε = pm.Uniform("σ_ε", lower=0, upper=1)
        Σ = pm.Normal("Σ", mu=drift + yearly, sd=σ_ε, observed=y)

        display(pm.model_to_graphviz(m))
        display(m)

    return m
