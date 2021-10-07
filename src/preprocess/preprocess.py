import logging

from src.preprocess.query_snowflake import read_meta, read_week_extremes

logger = logging.getLogger('SPARK')


def too_short(df_data, threshold=52):
    """
    Check if number of entries is long enough.

    Parameters
    ----------
    df_data: pd.DataFrame
        Data to check.
    threshold: int
        Minimum lenght.

    Returns
    -------
    bool
        True if preprocess is long enough.
    """
    logger.info(f"checking number of preprocess points (<={threshold})")
    if len(df_data) <= threshold:
        logger.info(f"number of preprocess points ({len(df_data)}) under threshold ({threshold})")
        return True
    else:
        return False


def too_small(df_data, capacity, threshold=0.25):
    """
    Check if values of preprocess is greater than threshold x capacity of transformer.

    Parameters
    ----------
    df_data: pd.DataFrame
        Data to check.
    capacity: int
        Capacity of the transformer.
    threshold: int
        Fraction of the capacity that should be reached.

    Returns
    -------
    bool
        True if preprocess exists that is greater than threshold x capacity.
    """
    logger.info(f"checking absolute values (<{threshold})")
    if df_data[["max", "min"]].abs().max().max() < capacity * threshold:
        logger.info(
            f"value of preprocess points are smaller than {threshold} times capacity ({capacity})"
        )
        return True
    else:
        return False


def remove_leading_idling(df_data, capacity, threshold=0.01):
    """
    Remove preprocess that was generated when DALI box was active but electrical connection was not.

    Parameters
    ----------
    df_data : ps.DataFrame
        Data to be cleaned.
    capacity: int
        Capacity of the transformer.
    threshold: int
        Fraction of the capacity that should be reached.

    Returns
    -------
    pd.DataFrame
        DataFrame without the idling preprocess points.
    """
    logger.info(f"removing leading low values (<{threshold})")
    df_data = df_data.sort_values(["year", "week"])
    df_mask = df_data[["max", "min"]].abs().max(axis=1) > capacity * threshold
    df_mask[df_mask.argmax():] = True
    return df_data.loc[df_mask]


def load_data(boxid):
    """
    Load preprocess and metadata for boxid and do preprocessing.

    Parameters
    ----------
    boxid: str
        ID of DALI box.

    Returns
    -------
    None | (df_data, df_meta)
        If checks are OK, return DataFrames with historic and meta preprocess.
    """
    go = True
    if go:
        # load meta preprocess and check availability
        df_meta = read_meta(boxid=boxid)
        if len(df_meta) == 0:
            logger.info(f"no meta preprocess available for boxid: {boxid}")
            go = False

    if go:
        # load week extremes and check availability
        df_data = read_week_extremes(boxid=boxid, L="sumli")
        if len(df_data) == 0:
            logger.info(f"no week extreme preprocess available for boxid: {boxid}")
            go = False
        else:
            capacity = df_meta["vermogen_nominaal"].squeeze()

    min_rows = 52 * 2
    max_loading = 0.50
    threshold_idling = 0.01
    # check preprocess requirements and clean preprocess
    if go:
        go = not too_short(df_data, threshold=min_rows)
    if go:
        go = not too_small(df_data, capacity, threshold=max_loading)
    if go:
        df_data = remove_leading_idling(df_data, capacity, threshold=threshold_idling)
        go = not too_short(df_data, threshold=min_rows)

    if go:
        return df_data, df_meta
