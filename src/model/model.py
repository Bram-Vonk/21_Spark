import numpy as np
import pymc3 as pm


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


def seasonality_model(t, p=52.1775, n=5, seasonality_prior_scale=10):
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
    x = polynomial(t, n=4)
    β = pm.Normal("β_drift", mu=0, sd=0.5, shape=n + 1)

    return pm.Deterministic("drift", det_dot(x, β))
