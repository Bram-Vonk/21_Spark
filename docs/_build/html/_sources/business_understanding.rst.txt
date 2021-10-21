Business Understanding
========

Business Objectives
----------
Enexis is a regulated DNO with a monopoly position regarding the distribution of electricity and gas.
The company wants to keep the delivery of electricity and gas:

* reliable
* affordable
* sustainable

This is realised by doing effective and efficient grid investments according to the Risk and Opportunity Based Asset Management method `[ROBAM] <https://www.enexis.nl/over-ons/-/media/documenten/diversen/ip/enexis-netbeheer-ip-g-2020-2030-publicatie.pdf?modified=20200514053144>`__.

Situation Assessment
----------

A changing environment
~~~~~~~~~~
| Power is delivered via grid components as cables and transformers (for electricity) to residential and industrial connections of our customers.
| These grid components have to have the needed capacity. This is monitored by Grid Planners and if needed transformers are swapped for heavier ones, or cable connections are strengthened.
| For decennia this monitoring was done by mainly looking to historical yearly extremes.
However, the increasing growth rate of power demand and supply driven by emerging technologies and electrification of transportation and heating, require a more frequent and pro-active electricity grid management.

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
~~~~~~~
| The more volatile and more rapidly increasing power flows require that Grid Planners more often monitor if the minimum and maximum power is still withing the transformer’s capacity. Otherwise, this will cause unsafe operating situations and it can lead to power outages.
| Grid Planners expect a big increase of the number of transformers that reach their operating capacity in the upcoming years. This in a environment were they are expected to make sure that Enexis is an enabler of the energy transition.

Opportunity for data science
~~~~~~~~~~
| Since a few years Enexis started to deploy so called Distribution Automation Light Boxes. With these measurement apparatus it is possible to monitor our distribution transformers near real time.
| At the moment of writing 11k distribution transformers (of the total population of 35k) are equipped with these apparatus which are measuring 15 minute average voltages, currents and powers of each transformer.
| This data (together with transformer metadata) enables to automatically detect or even foresee earlier overloading of transformers. It gives grid planners the opportunity to timely mitigate upcoming issues.


Data Mining Goals
----------

Primary objective
~~~~~~~~~~
| More volatile power flows require a monitoring tool that forecasts transformer overloading.
| The goal is to timely identify future overloading of transformers.

General description based on an example case
~~~~~~~~~~~
| The project should result in a tool that is able to predict in autumn that a transformer will be overloaded in spring due to EV with a prediction interval.
| The tool enables better planning of grid strengthening which prevents overloading of transformers (safety and reliability), foreseeing future work (costs) and enabling the energy transition better (sustainability).

Business Value Diagram
~~~~~~~~~~~~~~~~~
| Business value is created by the forecast model by enabling the preferred path for grid investments on the business value part (upper half) of the Business Flow Down Diagram below.
| This path is possible by providing grid planners with a probability that a transformer will overload in the foreseeable future.
| The model (lower half) will use historic DALI timeseries data to forecast transformer loading. By comparing this forecast with capacity of the transformer possible overloading can be foreseen.

.. image:: _static/img/value_flow_down.png
    :width: 800px
    :align: center

Business Flow Down Diagram for the project.

Requirements from Users
~~~~~~~~~~~~~~
The developed product is only valuable if it is use dby the end users, who are the Grid Planners.
Therefore the following additional requirements are important:

* Grid Planners don’t want another tool to log into/install..
* The presentation of results of the tool has to be quick (no long waiting times).
* The tool has to be scalable up to 35k transformers.
* The tool should be reliable (working itself and forecast should be accurate).
* Prediction intervals should be available to show the confidence of the forecast.
* Results should also be available for other tools (e.g. dashboarding via Power BI integration with the under construction project described at 7)
* There should be a way to sort transformers/forecasts based on their urgency.
* The measurement/forecast data should be exportable for other planning tools (such as Vision)
* It would be preferred if forecasts could also be made on transformers that have limited history of data with knowledge of the general population.
* Forecast horizon should be 6-12 months.
* The model used can be explained clearly.



Project Plan
----------

