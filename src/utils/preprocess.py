#  Copyright (c) 2021. Bram Vonk, Enexis

import numpy as np
import pandas as pd


def downcast(s, try_numeric=True, category=False):
    """
    Downcast  a series to the lowest possible memory type.

    Parameters
    ----------
    s : pd.Series
        Series to downcast.
    try_numeric: bool
        If True it will try to read strings as numeric values.
    category: bool
        If True (string) objects will be cast as a category.

    Returns
    -------
        Downcasted series.

    """
    if try_numeric:
        if s.dtype.kind != "M":
            s = pd.to_numeric(s, errors="ignore")

    if category:
        if s.dtype.kind == "O":
            s = s.astype("category")

    if s.dtype.kind == "f":
        s = pd.to_numeric(s, errors="ignore", downcast="float")
    elif s.dtype.kind == "i":
        s = pd.to_numeric(s, errors="ignore", downcast="signed")
        s = pd.to_numeric(s, errors="ignore", downcast="unsigned")

    return s


def map_labels(series, kind="categorical", labels=None, backwards=False, **arg):
    """
    Map a Series values by the labels given.

    Parameters
    ----------
    series: pd.Series
        Series to map on.
    kind: str
        Indicator for kind of preprocess in series. With kind of {"categorical", "ordinal"}  the mapping is applied,
        otherwise not.
    labels: dict
        Defines with the mapping {key_0: value_0, etc.}.
    arg:
        Additional arguments.

    Returns
    -------
    pd.Series
        Series with mapped values.
    """
    if kind in ["categorical", "ordinal"]:
        if isinstance(labels, dict):
            if backwards:
                labels = {v: k for k, v in labels.items()}
            series = series.map(labels)
    return series


class MinMaxScaler:
    """MinMax Scaler like in sklearn, prevents total library import/dependency."""

    def __init__(self, upper=1, lower=-1):
        """
        Initialize scaler with upper and lower boundary.

        Parameters
        ----------
        upper : float
            upper boundary to scale to
        lower : float
            lower boundary to scale to
        """
        self.upper = upper
        self.lower = lower
        self.max = None
        self.min = None

    def fit(self, X, y=None):
        """
        Get fit parameters.

        Parameters
        ----------
        X : np.array
            preprocess to fit on
        y : None
            solely for consistency

        Returns
        -------
        self
            instance with self.min, self.max defined.
        """
        self.max = np.max(X)
        self.min = np.min(X)
        return self

    def transform(self, X):
        """
        Scales preprocess according to fitted parameters.

        Parameters
        ----------
        X : np.array
            preprocess to scale

        Returns
        -------
        np.array
            scaled preprocess

        """
        X_01 = (X - self.min) / (self.max - self.min)
        return X_01 * (self.upper - self.lower) + self.lower

    def fit_transform(self, X, y=None):
        """
        Execute consecutively self.fit and self.transform.

        Parameters
        ----------
        X : np.array
            preprocess to scale
        y : None
            solely for consistency

        Returns
        -------
        np.array
            scaled preprocess

        """
        return self.fit(X).transform(X)

    def inverse_transform(self, X, y=None):
        """
        Scale back to original domain.

        Parameters
        ----------
        X : np.array
            preprocess to scale
        y : None
            solely for consistency

        Returns
        -------
        np.array
            scaled preprocess

        """
        X_xx = (X - self.lower) / (self.upper - self.lower)
        return X_xx * (self.max - self.min) + self.min
