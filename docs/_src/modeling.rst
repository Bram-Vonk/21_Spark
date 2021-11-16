Modeling
========


Modeling Technique
----------

The Grid Planners are looking to data driven forecast with a uncertainty indication as mentioned before.
This is visualized as a concept in the figure below.

 .. image:: _static/img/autumn_spring_load.png
    :width: 400px
    :align: center
A possible output of the model visualized.

Input Features
~~~~~~~~~~~~~
The Grid Planners want to have a result dat is based on real observed data.
Or, to make it more explicit: Data that has been measured and not data from possible scenarios with a wide range of uncertainty.

Another suggestion was made to use (historic) weather data as an exogenous feature / input for the model.
However, this is not data we have available with a reasonable confidence for the forecast horizon (in the future).
And seasonality can also be captured from the observed data itself for different timeseries models.

Therefore, the model only uses historic DALI measurement data.

Fit-Predict Process
~~~~~~~~~~~~~
A model will be fitted / tuned for every DALI measurement extremes since every transformer has it's own unique signal (:meth:`src.forecast.forecast.determine_estimates`).

A model is trained on observed data, a forecast is made and stored and finally the trained model is discarded (:meth:`src.forecast.forecast.forecast`).

.. image:: _static/img/process_modeling.png
    :height: 250px
    :align: center
The weekly extremes are loaded for tuning the model. The model forecasts are afterwards stored in a Snowflake database.

The next time a forecast is required, new data is available and a new model will be fitted and used for forecasting.

Model Environment
~~~~~~~~~~~~~~~
A probabilistic approach has been implemented to fulfill the wish to forecast and display uncertainty rather than a point estimate.

From the main probabilistic toolboxes (STAN, EDWARD2, Pyro, TensorFlow2 Probability) `PyMC3 <https://docs.pymc.io/en/stable/>`__ was used for it's extensive documentation.
A future step could be to transfer the model into TensorFlow2 Probability since PyMC3 is not the most recent toolbox anymore.

Generalized Additive Model Concept
~~~~~~~~~~~~~
To address the explainability of the model, a similar approach as `Facebook Prophet <https://facebook.github.io/prophet/>`__ is used.
The model is a Generalized Additive Model `(GAM) <https://en.wikipedia.org/wiki/Generalized_additive_model>`__ that consists of a trend / drift and seasonality component (and an error component).
The translation to PyMC3 of `Richie Vink <https://www.ritchievink.com/blog/2018/10/09/build-facebooks-prophet-in-pymc3-bayesian-time-series-analyis-with-generalized-additive-models/>`__ was used as a basis.

The GAM approach makes it easy to decompose the different components of the timeseries and show the Grid Planners the effect of the drift and seasons separately.



Test Design
----------
To evaluate the model the observed data is split into a train and test set based in the forecast horizon (:meth:`src.preprocess.preprocess.split_last`).
After splitting the train set is tested again for not being too short (at least two years: :meth:`src.preprocess.preprocess.too_short`).

 .. image:: _static/img/train_test.png
    :width: 600px
    :align: center
The split of measurement data into train and test data.

The test set is only used to validate forecasting results.
The train set is used to train / fit / tune the model.

Model
----------

Generalized Additive Model
~~~~~~~~~~~~~~~~

The GAM model used is (:meth:`src.model.model.create_model`):

.. math::
   \sigma_\epsilon \sim Uniform(lower=0, \:upper=1)

.. math::
   \Sigma\:|\:drift, yearly, \sigma_\epsilon = Normal(\mu=drift + yearly, \:sd=\sigma_\epsilon)

The additive naming is explicit in this notation.

The error component has a has a bandwidth of :math: `\sigma_\epsilon`.

Drift Component
^^^^^^^^^^^^^^

According to the Grid Planners a increasing growth is more and more common due to the energy transition.
Therefore, a stable drift model (:meth:`src.model.model.drift_model`) is used that can mimic that.
An exponential function resulted in divergence during the model tuning, but a second order taylor series makes the model convergent and stable.

The drift component model with a taylor series with the order of :math:`n` is described as:

.. math::
   X_{drift}(t) = [t^0, ...,  t^n]

.. math::
   \beta_{drift} \sim Normal(\mu=0, \:sd=0.5)

.. math::
   drift\:|\:\beta_{drift} = X_{drift}(t)\:\beta_{drift}

For modelling a drift that has the described growth, a polynomial with order :math:`n=2` is used.


Yearly Component
^^^^^^^^^^^^^^

Since the data has been aggregated into weekly extremes, the only seasonality to model is the yearly pattern.
The yearly seasonality is modeled with :math:`n` order fourier series (:meth:`src.model.model.seasonality_model`).
This based on the work of `Richie Vink <https://www.ritchievink.com/blog/2018/10/09/build-facebooks-prophet-in-pymc3-bayesian-time-series-analyis-with-generalized-additive-models/>`__.

The yearly seasonality model is described as:

.. math::
   X_{yearly}(t) = [cos(\frac{2 \pi 1 t}{T}), ..., sin(\frac{2 \pi n t}{T})]

.. math::
   \beta_{yearly} \sim Normal(\mu=0, \:sd=1)

.. math::
   drift\:|\:\beta_{yearly} = X_{yearly}(t)\:\beta_{yearly}

Here the :math:`T` is the period of the seasonality in unit of time of the data.
The is unit of time in case is a week for the data and a year in weeks is :math:`T=52.1775`.
The order taken for the fourier series is :math:`n=5`.

Enabling Forecasts
^^^^^^^^^^^^^^^^
The model parameters (:math:`\beta`)'s can now be tuned to produce the model is most likely to produce the observed (measurement) data.

To forecasting, the model also needs to produce beyond the timestamps it has been tuned on.
The PyMC3 model can cope with this by feeding it with timestamps that are extrapolated for the forecasting horizon (:meth:`src.preprocess.preprocess.extrapolate_timestamps`).

The matching observations (measurements) can be intentionally filled with NaN's. in the model PyMC3 will name them :math:`\Sigma_missing`.
(This characteristic makes the model also robust against missing data).

By sampling the posterior predictive after tuning, also samples are generated for the extrapolated forecast timestamps (:meth:`src.forecast.forecast.determine_estimates`).

Total model Σ
^^^^^^^^^^^^^^
 .. image:: _static/img/graph_model.png
    :width: 600px
    :align: center
The total model visualized.

Two separate GAM models :math:`\Sigma` (:meth:`src.model.model.create_model`) are used for the weekly minimum and maximum.

The visual above shows the total GAM model with a polynomial drift order :math:`n=2` (the bias of order 0 explains :math:`N+1=3`) and a fourier order of :math:`n=5` (the sine and cosine parts explain :math:`N*2=10`).

The number of observations (weeks of measurements for this case) is 121 and the forecasting horizon is just more than six months (27 weeks).

Formatting Results
^^^^^^^^^^^^^^^

From the model posterior predictive samples are drawn for all timestamps (also measurement timestamps, 1000 samples per timestamp).

From the posterior samples, the quantile bands are determined (:meth:`src.forecast.format.make_quantile_bands`).
This reduces the data storage.

The upper and lower limits of the quantile bands are then stored in the same format as the input (:meth:`src.forecast.format.format_model_estimates`).
The input of the model and the output are then concatenated together. This eases the visualization later.

 .. image:: _static/img/data_stored.png
    :width: 800px
    :align: center
The concatenated input and result.

Model Assessment
----------

The following model findings are most salient:

* The model converges during tuning and gives feasible results.
    * Exponential drift function tuning will not converge.
* The computational burden on a CPU to tune and forecast both extremes is 1:24.
    * CPU: 2 GHz Quad-Core Intel Core i5
    * RAM: 16 GB
* The model is fairly insensitive to outliers and missing data.
* The splitting of observations into train and test set works.
* The extrapolation with the forecasting horizon works.
* An pure additive model may not be sufficient.
    * Growth also increases the yearly component (see visualization below).
    * A pure multiplicative diverges.
    * A hybrid model (addition of a small fraction of a multiplicative model) might be an option.

A visualization of the results is shown in the figure below which shows most of the aforementioned points:

 .. image:: _static/img/additive_model.png
    :width: 800px
    :align: center
An visualization of the measurements (history) and forecast (estimates).
Measurements from the train and test set are plotted.

Improvement suggestions
~~~~~~~~~~~~~~~~~~~

The following ideas could result in a better model:

* A hybrid additive-multiplicative model for dealing with the growing seasonality.
* Adding a extra component to detect temporarily bypass switching of loads of other transformers.
    * This could be implemented by estimating parameters of a `rectangular function <https://en.wikipedia.org/wiki/Rectangular_function>`__.
* Making more recent observations more relevant for slowly changing loading patterns
    * Possibilities are to mimic weights with `pm.Potential <https://discourse.pymc.io/t/how-to-run-logistic-regression-with-weighted-samples/5689>`__ or `pm<distribution>(tau=weights) <https://discourse.pymc.io/t/pm-sample-posterior-predictive-not-working-with-weights/5698/11>`__.
* Use the population seasonality as a `prior <https://minimizeregret.com/post/2019/04/16/modeling-short-time-series-with-prior-knowledge/>`__ in case of a short history of observations.
* Use by-pass dummy model for `outlier robustness <https://docs.pymc.io/en/stable/pymc-examples/examples/generalized_linear_models/GLM-robust-with-outlier-detection.html>`__.
