import asyncio
import datetime
import datetime as dt
import platform
from os import getenv
from typing import Callable

import aiohttp
import pandas as pd
from flask import Flask, jsonify, request

from data_collectors import isw_data_collector
from isw_data_modeling import main as main_isw_modeling, process_file_data
from alarm_data_modeling import main as main_alarm_modeling
from data_collectors.isw_data_collector import get_report_for_date
from isw_data_preparation import main as main_isw_preparation, prepare_report
from merge import main as main_merge, merge_weather_alarm_keywords_for_files, ALARMS_DATA_FILE
from separate_test_data import main as main_separate_data
from train_model import train_models
from tune_model import tune_models


from ml.prediction import update_prediction_for_next_12_hours
from ml.storage import save_predictions, get_predictions


# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = getenv('API_TOKEN')
if API_TOKEN is None:
    raise RuntimeError("API_TOKEN must be provided from env variables.")

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    @property
    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def authorize_and_validate_request(f: Callable):
    def wrapper():
        json_data = request.get_json()

        if json_data.get("token") is None:
            raise InvalidUsage("token is required", status_code=400)

        token = json_data.get("token")

        if token != API_TOKEN:
            raise InvalidUsage("wrong API token", status_code=403)

        return f()

    wrapper.__name__ = f.__name__
    return wrapper


def add_execution_time_params_to_response(f: Callable[[], dict]):
    def wrapper():
        start_dt = dt.datetime.now()
        response = f()
        end_dt = dt.datetime.now()
        execution_time_params = {
            "event_start_datetime": start_dt.isoformat(),
            "event_finished_datetime": end_dt.isoformat(),
            "event_duration": str(end_dt - start_dt),
        }
        response.update(execution_time_params)
        return response

    wrapper.__name__ = f.__name__
    return wrapper


async def index():
    await collect_data()
    main_isw_preparation()
    main_isw_modeling()
    main_alarm_modeling()
    main_merge()
    main_separate_data()
    train_models()
    tune_models()


def update_forecast():
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

    report_path = asyncio.run(get_report_for_date(yesterday))
    csv_path = prepare_report(report_path)
    isw_data_csv_path = process_file_data(csv_path)
    df = merge_weather_alarm_keywords_for_files(n, ALARMS_DATA_FILE, isw_data_csv_path, yesterday)

    df['datetimeEpoch'] = pd.to_datetime(df['day_datetime'] + ' ' + df['hour_datetime'])
    df['datetimeEpoch'] = (df.datetimeEpoch - datetime.datetime(1970, 1, 1)).dt.total_seconds().astype(int)
    df.set_index('datetimeEpoch', inplace=True)
    df = df.drop(labels=['is_alarm'], axis=1)

    data = update_prediction_for_next_12_hours()
    data_vals = data.values.tolist()
    save_predictions(data_vals)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict)
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return '<p><h2>Alarms forecasting app</h2></p>'


@app.route(
    '/content/api/v1/integration/forecast/update',
    methods=["POST"],
)
@authorize_and_validate_request
@add_execution_time_params_to_response
def update_forecast_endpoint():
    update_forecast()
    return jsonify(status="OK")


@app.route(
    '/content/api/v1/integration/forecast/alarms',
    methods=["POST"],
)
@authorize_and_validate_request
@add_execution_time_params_to_response
def get_forecast_endpoint():
    regions = request.json['regions'] if 'regions' in request.json else []
    try:
        predictions = get_predictions(regions)
        result = {
            "last_model_train_time": "2023-02-01T13:15:30Z",  # time when model was retrained last time
            "last_prediciotn_time": "2023-04-01T13:15:30Z",  # time when the prediction was updated
            "regions_forecast": predictions
        }
        return result
    except FileNotFoundError:
        return {"Error": "You must update the prediction first. /content/api/v1/integration/forecast/update"}, 400
