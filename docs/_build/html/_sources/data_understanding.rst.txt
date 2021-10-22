Data Understanding
========



Initial Data Collection
----------

The goal is to forecast accurately maximum and minimum loading of transformers.
There is 15 minute average data available of 11k transformers. The maximum and minimum loading is not needed on this detailed level.
According to the Grid Planners, weekly or monthly extreme details are more than enough.

For this first model to forecast transfer loading no external variables will be used as input for the model.
Only historic data will be used (with metadata to extract de capacity of the transformer).

Data is available in Snowflake. in a Jupyter Notebook pandas with a SQLAlchemy engine is used for the data collection from Snowflake.
Credentials are available via Vault in the Enexis domain.

Measurement data source
~~~~~~~~~~~~~

In a Snowflake database the following data is available:

.. list-table:: Snowflake data source details.
   :widths: 25 25
   :header-rows: 0

   * - Database
     - DB_CDWH_P
   * - Schema
     - CDWH_4_BDM
   * - Table
     - BDM_DALI_METINGEN


Meta data source
~~~~~~~~~~~~~

In a Snowflake database the following metadata is available:

.. list-table:: Snowflake data source details.
   :widths: 25 25
   :header-rows: 0

   * - Database
     - DB_CDWH_P
   * - Schema
     - CDWH_5_INF_MEETDATA_E View: DIM_DALI_BOX_VW
   * - Table
     - DIM_DALI_BOX_VW



Data Description
----------

Measurement data details
~~~~~~~~~~~~~

| The measurements are available since Q2 2018. Since then more and more transformers were equiped with DALI boxes and at the moment of writing (Q3 2021) a total number of 10,992 boxes are measured
| Measurements on open doors (from safety perspective important) and currents, voltages and powers accumulated up to 89,052,020,404 records in the Snowflake table.

| For this project we focus first on the active power on a transformer om the medium voltage connection side. The power is available for all three power phases as well as the sum of them.
| Below are the fields of interest given that are queried from the aforementioned table.


.. list-table:: DALI table fields of interest.
   :widths: 25 25 50
   :header-rows: 1

   * - Field o.i.
     - Type
     - Example
   * - BOXID
     - VARCHAR
     - ESD.000240-2
   * - CHANNELID
     - VARCHAR
     - register://electricity/0/activepower/sumli?avg=15
   * - WAARDE
     - DOUBLE
     - -3.408062
   * - DATUMTIJD
     - TIMESTAMPTZ
     - 2021-05-12 07:45:00.000000000


Measurement data details
~~~~~~~~~~~~~

| In the metadata table there are 15,058 records present.
| Only 10.092 boxids are operational and have a nominal power correctly registered.

.. list-table:: Metadata table fields of interest.
   :widths: 25 25 50
   :header-rows: 1

   * - Field o.i.
     - Type
     - Example
   * - BOXID
     - VARCHAR
     - ESD.000240-2
   * - BOX_BEDRIJFSSTATUS
     - VARCHAR
     - in bedrijf
   * - IN_BEDRIJFSNAME_DATUMTIJD
     - TIMESTAMPTZ
     - 2021-05-12 07:45:00.000000000
   * - VESTIGING
     - VARCHAR
     - Breda
   * - VERMOGEN_NOMINAAL
     - NUMBER
     - 400

Data Exploration
----------

The measurement data is up-to-date, but has missing values in two moments in time (both in 2021). This issue was discovered and is addressed.
For the project it won't be a huge issue, since the data is aggregated to weekly extremes.
This will cause extremes to be less extreme if (a lot of) data is missing. Only if data is missing for a whole week, there will also be missing data in the aggregated set.
In both cases (outlier and missing data) the model can handle this.

For timeseries modelling it is advised to have at least two periods (years in this case) of measurement data.
As the figure below shows, this might be a problem eventually. One of the challenges is therefore to explore if prior knowledge of the population can overcome this issue.

In the figure below the completeness of the data over time is given for the transformers in the area of Breda.
On the vertical axis the transformers are shown ordered by the time they got operational. On the horizontal axis the time is given. In color the completeness is given per week: Darkblue (value 1) means that all data was present, towards white (value 0) means no data at all.


.. image:: _static/img/dq_completeness.jpeg
    :width: 800px
    :align: center

Completeness for DALI data in the service area of Breda.


Data Quality
----------

Beside the missing data described above, the data quality (of the 15 minute power averages) seems like expected.
The reason is probably that the 15 minute averaging already smooths out the extreme (short circuit) values and measurement errors. Although sometimes outliers can still be seen in the data (which can propagate into the weekly extremes as shown on the figure below).
Taking not only the extremes, but also the second highest/lowest value per week for robustness did not make a lot of difference (probably also due to the aforementioned smoothing).

.. image:: _static/img/dq_outlier.png
    :width: 800px
    :align: center

Example of weekly extremes with an outlier for the maximum in July 2020.
