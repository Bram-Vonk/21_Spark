#  Copyright (c) 2021. Bram Vonk, Enexis

import datetime as dt
import logging
import os

import pandas as pd
import pytz
import snowflake.connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

from src.utils.parser import parse_config
from src.utils.preprocess import downcast
from src.utils.vault import get_secrets

logger = logging.getLogger("SPARK")

config = parse_config(os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), "../settings.yml"))))

channel_like = "register://electricity/0/activepower/%?avg=15"
column_details = """
(BOXID VARCHAR(50), L VARCHAR(5),
YEAR NUMBER(4), WEEK NUMBER(2),
PROCESSED_ON TIMESTAMP_TZ,
MAX DOUBLE, MIN DOUBLE)
"""


def format_connection(name):
    """
    Get (connection) details in the right format for different tables.

    Parameters
    ----------
    name : name of the different sources

    Returns
    -------
    Connection
    """
    con_config = get_secrets("snowflake")
    con_config.update(config["snowflake"][name])
    return con_config


def read_meta(boxid=None):
    """
    Read meta preprocess of DALI box.

    Parameters
    ----------
    boxid : list
        ID of DALI box to read.
        None results in all available preprocess of DALI boxes that have nominal power specified.

    Returns
    -------
    pd.DataFrame with metadata.
    """
    logger.info("reading meta preprocess")
    con_config = format_connection("DALI_meta")

    if boxid is None:
        logger.info("for all boxids")
        box_selector = ""
    else:
        logger.info(f"for boxids: {boxid}")
        if isinstance(boxid, (str)):
            boxid = [boxid]
        s = ", ".join([f"'{s}'" for s in boxid])
        box_selector = f"AND t.BOXID IN ({s})"

    query = f"""
    SELECT
           t.BOXID,
           t.TRAFO_FUNCTIEPLAATS_ID,
           t.VERMOGEN_NOMINAAL,
           t.TRAPSTAND_INGESTELD,
           t.STATIONSNUMMER,
           t.TRAFO_FUNCTIEPLAATS_ID,
           t.STATIONSNAAM,
           t.STATIONSFUNCTIE,
           t.REGIO_NETAUTOMATISERING,
           t.VESTIGING,
           t.PLAATS,
           t.STRAAT,
           t.HUISNUMMER,
           t.POSTCODE,
           t.GEMEENTE,
           t.LAT,
           t."LONG",
           t.STATION_BEDRIJFSSTATUS,
           t.BOX_BEDRIJFSSTATUS,
           t.IN_BEDRIJFSNAME_DATUMTIJD,
           t.LAATSTE_PROVISIONINGSSTATUS
    FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]} t
    WHERE  t.STATION_BEDRIJFSSTATUS ILIKE 'in bedrijf'
          AND t.BOX_BEDRIJFSSTATUS ILIKE 'in bedrijf'
          AND t.VERMOGEN_NOMINAAL IS NOT NULL
          {box_selector}
    """

    with create_engine(URL(**con_config)).connect() as con:
        df_query = pd.read_sql(sql=query, con=con)

    return df_query


def make_week_extremes_query(boxid=None, last_processed=dt.datetime(2001, 1, 1)):
    """
    Build the query to request week extremes.

    Parameters
    ----------
    boxid : list
        If not None: select specific boxes.
    last_processed: datetime
        Date to determine week extremes from. Cuts are always made on the last monday.

    Returns
    -------
    str
        Query string.
    """
    con_config = format_connection("DALI_data")

    if boxid is None:
        box_selector = ""
    else:
        if isinstance(boxid, (str)):
            boxid = [boxid]
        s = ", ".join([f"'{s}'" for s in boxid])
        box_selector = f"AND t.BOXID IN ({s})"

    query = f"""
    SELECT
        t.BOXID AS BOXID,
        REGEXP_SUBSTR(t.CHANNELID, '(sumli|l[1,2,3])') AS CHANNELID,
        YEAROFWEEKISO(t.DATUMTIJD) AS YEAR,
        WEEKISO(t.DATUMTIJD) AS WEEK,
        CURRENT_TIMESTAMP AS PROCESSED_ON,
        MAX(t.WAARDE) AS MAX_VALUE,
        MIN(t.WAARDE) AS MIN_VALUE
    FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]} t
        WHERE t.CHANNELID LIKE '{channel_like}'
         AND t.DATUMTIJD >= DATEADD(DAY, -DAYOFWEEKISO(DATE('{last_processed}')), DATE('{last_processed}'))
         AND t.DATUMTIJD < DATEADD(DAY, -DAYOFWEEKISO(CURRENT_DATE), CURRENT_DATE)
         {box_selector}
    GROUP BY t.BOXID, t.CHANNELID, YEAROFWEEKISO(t.DATUMTIJD), WEEKISO(t.DATUMTIJD)
    """

    return query


def create_table_query(query):
    """
    Make query to create or replace table and insert preprocess of select query.

    Parameters
    ----------
    query : str
        Select query to be used.

    Returns
    -------
    str
        New query

    """
    con_config = format_connection("DALI_extremes")
    query = f"""
    CREATE OR REPLACE TABLE
        {con_config["database"]}.{con_config["schema"]}.{con_config["table"]}
        {column_details}
        CLUSTER BY (BOXID, L)
        COPY GRANTS
        AS ({query})
    """

    return query


def insert_table_query(query):
    """
    Make query to insert preprocess of select query in an existing table.

    Parameters
    ----------
    query : str
        Select query to be used.

    Returns
    -------
    str
        New query

    """
    con_config = format_connection("DALI_extremes")
    query = f"""
    INSERT INTO
        {con_config["database"]}.{con_config["schema"]}.{con_config["table"]}
        ({query})
    """

    return query


def create_week_extremes():
    """Execute query to create whole new table of week extremes asynchroniously."""
    logger.info("creating new extremes table of total history")
    query = create_table_query(make_week_extremes_query())

    with snowflake.connector.connect(**get_secrets("snowflake")) as con:
        con.cursor().execute_async(query)


def get_last_processed_time():
    """
    Retrieve last time table update has been done.

    Returns
    -------
    datetime
        Last processing time.

    """
    logger.info("retrieving last update on extremes table")
    con_config = format_connection("DALI_extremes")
    query = f"""
        SELECT MAX(t.PROCESSED_ON)
        FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]} t
    """

    with snowflake.connector.connect(**get_secrets("snowflake")) as con:
        last_processed = con.cursor().execute(query).fetchone()[0]
        logger.info(f"last update on extremes table: {last_processed}")
        return last_processed


def update_week_extremes():
    """Update week extremes from last processing time upt o last monday."""
    logger.info("updateing extremes table")

    last_processed = get_last_processed_time()

    if last_processed.date().isocalendar()[:2] == dt.datetime.now().date().isocalendar()[:2]:
        logger.info("extremes table is up to date")
        pass
    else:
        logger.info(f"updating from {last_processed}")
        query = insert_table_query(make_week_extremes_query(last_processed=last_processed))

        with snowflake.connector.connect(**get_secrets("snowflake")) as con:
            # con.cursor().execute_async(query)
            con.cursor().execute(query)


def read_week_extremes(boxid=None, L=None):
    """
    Read week extremes for a DALI box and phase.

    Parameters
    ----------
    boxid: list
        If not None: A list with DALI box IDs to read.
    L: str
        The phases to retrieve (sumli, L1, L2, L3)

    Returns
    -------
    pd.DataFrame
        Week extremes.
    """
    logger.info("reading extremes table")
    con_config = format_connection("DALI_extremes")

    if boxid is None:
        logging.info("for all boxids")
        box_selector = ""
    else:
        logging.info(f"for boxids: {boxid}")
        if isinstance(boxid, (str)):
            boxid = [boxid]
        s = ", ".join([f"'{s}'" for s in boxid])
        box_selector = f"AND t.BOXID IN ({s})"

    if L is None:
        logging.info("for all phases")
        phase_selector = ""
    else:
        logging.info(f"for phases: {L}")
        if isinstance(L, (str)):
            L = [L]
        s = ", ".join([f"'{s}'" for s in L])
        phase_selector = f"AND t.L IN ({s})"

    query = f"""
    SELECT
        t.*
    FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]} t
        WHERE TRUE {box_selector} {phase_selector}
    """

    with create_engine(URL(**con_config)).connect() as con:
        df_query = pd.read_sql(sql=query, con=con)

    df_query = df_query.apply(downcast, try_numeric=True, category=False)

    if len(df_query):
        df_query["date"] = df_query.apply(lambda df: dt.datetime.fromisocalendar(df["year"], df["week"], 1), axis=1)
    else:
        df_query = df_query.assign(date=None)

    return df_query


def clear_forecasts():
    """
    Clear the table with forecasts.

    Returns
    -------
    None
    """
    con_config = format_connection("DALI_forecasts")

    query = f"""
    CREATE OR REPLACE TABLE {con_config["database"]}.{con_config["schema"]}.{con_config["table"]}
        (
            BOXID        VARCHAR(50),
            DATE         TIMESTAMPNTZ,
            L            VARCHAR(5),
            PROCESSED_ON TIMESTAMPNTZ,
            WEEK         NUMBER(2),
            YEAR         NUMBER(4),
            EXTREME      VARCHAR(3),
            VALUE        DOUBLE,
            PERIOD       VARCHAR(10),
            MODEL_VAR    VARCHAR(10),
            BAND         VARCHAR(10),
            BOUNDARY     VARCHAR(10),
            IS_VALID     BOOLEAN
        )
        CLUSTER BY (BOXID, L)
        COPY GRANTS;
    """

    with snowflake.connector.connect(**get_secrets("snowflake")) as con:
        con.cursor().execute(query)


def clear_forecast_meta():
    """
    Clear the table with forecast metadata.

    Returns
    -------
    None
    """
    con_config = format_connection("DALI_forecast_meta")

    query = f"""
    CREATE OR REPLACE TABLE {con_config["database"]}.{con_config["schema"]}.{con_config["table"]}
        (
            BOXID               VARCHAR(50),
            STATIONSNUMMER      VARCHAR(50),
            REGIO               VARCHAR(50),
            VESTIGING           VARCHAR(50),
            L                   VARCHAR(5),
            PROCESSED_ON        TIMESTAMPNTZ,
            VERMOGEN_NOMINAAL   NUMBER,
            RELATIVE_ABS_MAX    DOUBLE,
            DATE_ABS_MAX        DATE
        )
        CLUSTER BY (BOXID)
        COPY GRANTS;
    """

    with snowflake.connector.connect(**get_secrets("snowflake")) as con:
        con.cursor().execute(query)


def write_forecasts(df):
    """
    Write results into the Snowflake database.

    Parameters
    ----------
    df: pd.DataFrame
        Results to write.

    Returns
    -------
    None
    """
    df["processed_on"] = dt.datetime.now(tz=pytz.timezone("UTC"))
    df["is_valid"] = True

    con_config = format_connection("DALI_forecasts")

    with create_engine(URL(**con_config)).connect() as con:
        df.to_sql(
            name=con_config["table"],
            con=con,
            schema=con_config["schema"],
            if_exists="append",
            index=False,
        )


def write_forecast_meta(df):
    """
    Write assessment of forecast on capacity to forecast metadata table in Snowflake.

    Parameters
    ----------
    df: pd.DataFrame
        Assessment results.

    Returns
    -------
    None
    """
    con_config = format_connection("DALI_forecast_meta")

    with create_engine(URL(**con_config)).connect() as con:
        df.to_sql(
            name=con_config["table"],
            con=con,
            schema=con_config["schema"],
            if_exists="append",
            index=False,
        )


def read_forecasts(boxid=None):
    """
    Read forecasts for Snowflake database.

    Parameters
    ----------
    boxid: str
        Boxid of a DALI box. If not provided or None, all forecast are loaded.

    Returns
    -------
    pd.DataFrame
        DataFrame with forecasts.
    """
    con_config = format_connection("DALI_forecasts")

    if boxid is None:
        logging.info("for all boxids")
        box_selector = ""
    else:
        logging.info(f"for boxids: {boxid}")
        if isinstance(boxid, (str)):
            boxid = [boxid]
        s = ", ".join([f"'{s}'" for s in boxid])
        box_selector = f"AND t.BOXID IN ({s})"

    query = f"""
    SELECT
        t.*
    FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]} t
        WHERE IS_VALID  {box_selector};
    """

    # with create_engine(URL(**con_config)).connect() as con:
    #     df_query = pd.read_sql(sql=query, con=con)
    with snowflake.connector.connect(**get_secrets("snowflake")) as con:
        # con.autocommit(True)
        cur = con.cursor()
        cur.execute(query)
        df_query = cur.fetch_pandas_all()
        # con.commit()

    return df_query.rename(columns=str.lower)


def read_forecast_meta():
    """
    Read assessment of forecasts.

    Returns
    -------
    pd.DataFrame
        Results of he assessment of all DALI box forecasts.
    """
    con_config = format_connection("DALI_forecast_meta")

    query = f"""
        SELECT
            t.*
        FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]} t
        """

    with create_engine(URL(**con_config)).connect() as con:
        df_query = pd.read_sql(sql=query, con=con)

    return df_query.rename(columns=str.lower)


def get_forecasted_boxids():
    """
    Get the boxids for boxes that are already forecasted.

    (Should be adapted when multiple forecasts (done on different dates) are present in database).

    Returns
    -------
    pd.DataFrame
        Unique boxids.
    """
    con_config = format_connection("DALI_forecasts")

    query = f"""
    SELECT DISTINCT(BOXID)
    FROM {con_config["database"]}.{con_config["schema"]}.{con_config["table"]}
    """

    with create_engine(URL(**con_config)).connect() as con:
        df_query = pd.read_sql(sql=query, con=con)

    return df_query
