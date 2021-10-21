Business Understanding
========

Business Objectives
----------

Situation Assessment
----------

Data Mining Goals
----------

Project Plan
----------

Within the current society we are used to and dependent on a reliable and affordably energy supply. Also, we see an increase of:

- Electric energy production on the customer side, for instance, by installing Photo Voltaic (PV) panels, leading to a bi-directional electricity flow.
- Number of users of electrical vehicles (EVs) leading to more than double the electricity consumption.
- Sustainable production plants leading to a larger share of volatile and less predictable electricity production from the supplier side.

Preventing capacity problems in the electricity grid is one of the main challenges of Dutch Network operators.
The business needs predictions of electricity demand to select potential congestion areas.
In these areas flexible load is offered for managing congestions.

Another challenge is to make forecasts widely available. Especially in case the business needs tons of forecasts.

Therefore, we worked on:

- Extracting and transforming time series data from sensors.
- Combining this with weather forecasts.
- Engineering of time based features.
- Forecasting the electricity load.
- Monitoring training experiments and model performances
- Deploying scripts to a scalable production environment

The end result are *Forecasts as a Service* in production that generates predictions on a 15-min interval for 1000+ forecast signals.
These predictions are used by decision makers to offer flexible load and to prevent potential congestions.

.. image:: _static/img/FaaS.png
    :width: 800px
    :align: center

Business Understanding
----------------------