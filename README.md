# 21_Spark

![](images/BV.png)

Personal JADS project of Bram Vonk called [Spark](https://en.wiktionary.org/wiki/sp%C3%A1) that covers medium-term load forecasting on DALI data.

See the [documentation](https://bram-vonk.github.io/21_Spark) for more details.

![](docs/_src/_static/img/process_triggered.png)

The main steps are depicted above. These steps can be run via a Docker container:
* run `docker-compose run update_extremes` for to update the table with weekly extremes.
* run `docker-compose run make_forecasts ` to tune the model, forecast transformer loadings and store the results.
* run `docker-compose run -p 8000:8000 dashboard` to provide a dashboard to view results.