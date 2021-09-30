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
        Indicator for kind of data in series. With kind of {"categorical", "ordinal"}  the mapping is applied,
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
