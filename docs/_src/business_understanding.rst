Business Understanding
======================

Business Objectives
-------------------

Enexis is a regulated DNO with a monopoly position regarding the distribution of electricity and gas.

The company wants to keep the delivery of electricity and gas:

* reliable
* affordable
* sustainable

This is realised by doing effective and efficient grid investments according to the Risk and Opportunity Based Asset Management method `[ROBAM] <https://www.enexis.nl/over-ons/-/media/documenten/diversen/ip/enexis-netbeheer-ip-g-2020-2030-publicatie.pdf?modified=20200514053144>`__.

Situation Assessment
--------------------


A changing environment
~~~~~~~~~~~~~~~~~~~~~~

Power is delivered via grid components such as cables and transformers (for electricity) to residential and industrial connections of our customers.

The capacity of these grid components should always be sufficient for the power flows in the grid. This is monitored by Grid Planners and if needed transformers are swapped for heavier ones, or cable connections are strengthened.

For decades this monitoring was done mainly by looking to historical yearly extremes.

However, the increasing growth rate of power demand and supply driven by emerging technologies as electrical vehicles (EV) and photovoltaics (PV), requires shorter monitoring periods and nowadays even forecasts.
Otherwise, there is no time for mitigating actions and customers will be out of power.

.. image:: _static/img/pv_cbs.png
    :width: 400px
    :align: center

Solar power (PV) in The Netherlands (source: `CBS <https://www.cbs.nl/nl-nl/nieuws/2020/10/productie-groene-elektriciteit-in-stroomversnelling>`__).

.. image:: _static/img/ev_rvo.png
    :width: 400px
    :align: center

Battery (B), Fuel Cell (FC) and Plugg-in Hybride (PH) Electric Vehicles (EV) in The Netherlands (source: `RVO <https://www.rvo.nl/sites/default/files/2021/03/Elektrisch Rijden op - de - weg - voertuigen en laadpunten - jaaroverzicht 2020.pdf>`__).

.. image:: _static/img/hp_cbs.png
    :width: 400px
    :align: center

Installed power of heat pumps (HP) in The Netherlands (source: `CBS <https://opendata.cbs.nl/statline/#/CBS/nl/dataset/82380NED/line?dl=55480>`__).


Impact on grid management
~~~~~~~~~~~~~~~~~~~~~~~~~

The more volatile and more rapidly increasing power flows, require Grid Planners more often to monitor if the minimum and maximum power is still within the transformer’s capacity.
Otherwise, this will cause unsafe operating situations and it can lead to power outages.

Grid Planners expect a big increase of the number of transformers that reach their operating capacity in the upcoming years.
This in a time and environment where Grid Planners are expected to make sure that Enexis is an enabler of the energy transition and not a show stopper.


Opportunity for data science
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since a few years Enexis started to deploy so called Distribution Automation Light Boxes (DALI).

With these measurement apparatus it is possible to monitor our distribution transformers near real time.

At the moment of writing 11k distribution transformers (of the total population of 35k) are equipped with these apparatus which are measuring 15 minute average voltages, currents and powers of each transformer.

This data (together with transformer metadata) enables us to automatically detect or even foresee earlier overloading of transformers.
It gives grid planners the opportunity to timely mitigate upcoming issues.


Data Mining Goals
-----------------

Primary objective
~~~~~~~~~~~~~~~~~

More volatile power flows require a monitoring tool that forecasts transformer overloading.

The goal is to timely identify future overloading of transformers.


Example Use Case
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project should result in a tool that is able to predict in autumn that a transformer will be overloaded in spring due to EV with a prediction interval.

The tool enables better planning of grid strengthening which prevents overloading of transformers (safety and reliability), foreseeing and better plan future work (costs) and enabling the energy transition better (sustainability).


Business Value Diagram
~~~~~~~~~~~~~~~~~~~~~~

Business value is created by the forecast model by enabling the preferred path for grid investments on the business value part (upper half) of the Business Flow Down Diagram below.

This path is possible by providing grid planners with a probability that a transformer will overload in the foreseeable future.

The model (lower half) will use historic DALI timeseries data to forecast transformer loading.
By comparing this forecast with capacity of the transformer possible overloading can be foreseen.

.. image:: _static/img/value_flow_down.png
    :width: 800px
    :align: center

Business Flow Down Diagram for the project.


Requirements from Users
~~~~~~~~~~~~~~~~~~~~~~~

The developed product is only valuable if it is used by the end users, who are the Grid Planners.
Therefore the following additional requirements and wishes are important:

* Grid Planners don’t want another tool to log into/install..
* The presentation of results has to be quick (no long waiting times).
* Results have to scalable up to 35k transformers.
* The tool should be reliable (stable interface and accurate forecasts).
* The model should be explainable.
* The uncertainty of predictions should be available.
* Results should be available for further use (e.g. importable for load flow tools).
* The results should be sorted based on their urgency.
* Forecast can also be made with limited transformer data.
* Forecast horizon should be six months.


Success Criteria
~~~~~~~~~~~~~~~~

The project is a success if there is a tool that is being used by the Grid Planners that accurately forecasts overloading of transformers.

Usage of the tool can be measured by tracking users of the tool and by performing interviews with the end users after deployment.
Accuracy is assessed by comparing forecasts with measurements.

In more detail the project is a success if:

* The model forecasts prediction intervals.
* The working of the model can be explained clearly.
* The prediction intervals ranges are acceptable to the Grid Planners.
* The model can use prior information of the rest of the population if historic measurements are missing.
* The computational burden is acceptable.


Project Plan
------------

Organisation
~~~~~~~~~~~~

The involved stakeholders are:

* Grid Planners
    * The end users of the tool. Ad hoc, they will be updated/asked for input/their expertise on the field of grid planning and their needs. They assess if the project is a success.
* Data Engineers
    * To get the tool into production the ICT guidelines and processes within Enexis have to be respected. Expertise of the Data engineers is crucial in the second half of the project to get things into production/deployment.
* Management
    * The direct manager enables Developer/Lead Bram to work two days a week on this project. Together with all other Enexis stakeholders they will be updated at the end of every sprint in the sprint review session.
* Academic supervision:
    * Jeroen de Mast will be the academic director that monitors progress and the academic level. Every three weeks there will be an one-on-one meeting to discuss progress and issues.
* Academic support:
    * PDEng candidate Akshaya Ravi of JADS is available for support on technical and academic issues. Together with a buddy from the Lead Track periodic meetings (every four weeks) will be planned, but also ad hoc issues will be discussed directly.

.. image:: _static/img/stakeholders.png
    :width: 600px
    :align: center

The Stakeholders with meeting frequencies (heartbeat / ad hoc).


Resources
~~~~~~~~~

The project will take place in June, July, September, October and November 2021.

* Personnel
    * Project lead / developer: Available 2 days per week.
    * Grid Planners: Available 2 hours per week.
    * Data engineers: Available 2 hours per week in October - November.
    * Supervision / support: Both available for a few hours every 3 weeks.

* Data
    * DALI 15-minute measurement data.
    * Distribution transformer metadata (capacity).


Requirements
~~~~~~~~~~~~

The tool should be implemented in such way that it is:

* Maintainable: The code has to have docstrings and unit tests.
* Scalable: The tool has to be able to process 35k transformers.
* Deployable: The tool has to be able to go in production according to the Enexis standards (Test-Acceptance-Production).


Assumptions
~~~~~~~~~~~

* DALI data is available without huge quality issues during the project.
* Weekly extremes on transformer data is an acceptable aggregation level for capacity planning.
* Data Engineering has capacity for several hours a week for support between September and December.
* The computational burden for probabilistic models is feasible regarding the computational power available.


Risks and Contingencies
~~~~~~~~~~~~~~~~~~~~~~~

* Lead / developer has just become a father (is technically up to September on parental leave) and bought a house that has to be renovated. This could result in lower availability for this project.

    * Mitigation: None.

* Grid Planners are immensely preoccupied with the current challenges in the grid. Although not a lot of time is required, it might be that other activities have higher priority than this project.

    * Mitigation: Be clear and direct regarding expectations and communications and limit the effort and time for this project for Grid Planners without giving in on quality/input.

* Data Engineers are also loaded with work and might not have time/resources available.

    * Mitigation: It is essential to request capacity in the beginning of the project, although they will be involved only in the second half.

* There is no use of sensitive data in this project regarding privacy (GDPR) or security. DALI data is allowed to be used. Credentials are not embedded in code and access to data sources is restricted by design.


Costs and Benefits
~~~~~~~~~~~~~~~~~~

* Data collection
    * Data is available in an existing database. Only querying is needed, no active additional data collection.
* Implementation
    * Open source software is used besides already licensed applications. Only computation power will cost additionally. More details will be available after a first proof of concept.


Implementation Concept
~~~~~~~~~~~~~~~~~~~~~~

The tool is split into three steps to tackle the amount of data available, but still make the results manageable:

* Preprocessing
    * To condense 15 minute load averages into weekly extremes (minimum and maximum).
* Forecasting
    * To fit a model on the aggregated data and create forecasts.
* Dashboarding
    * To display (forecast) results to the end user.

In between steps results are stored in a Snowflake database.

.. image:: _static/img/process_steps.png
    :width: 800px
    :align: center

The proposed steps for implementation of the tool.


Planned Milestones
~~~~~~~~~~~~~~~~~~

.. list-table:: Scheduled project milestones for 2021.
   :widths: 25 25 50
   :header-rows: 1

   * - week
     - CRISP-DM step
     - detail
   * - 26
     - Business Understanding
     -
   * - 29
     - Data understanding
     - Go / No Go
   * - --
     - --
     - Summer break
   * - 36
     - Data Preparation
     -
   * - 39
     - Modeling
     -
   * - 42
     - Evaluation
     - Go / No Go
   * - 45
     - Deployment
     -





