import datetime
import datetime as dt
from os import getenv
from typing import Callable

from flask import Flask, jsonify, request

from ml.prediction import update_prediction_for_next_12_hours
from ml.storage import get_predictions, save_predictions


WEATHER_API_KEY = getenv('WEATHER_API_KEY')

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = getenv('API_TOKEN')
if API_TOKEN is None:
    raise RuntimeError("API_TOKEN must be provided from env variables.")

app = Flask(__name__)

last_prediction_time = datetime.datetime.min
# last_prediction_time = datetime.datetime.now() - datetime.timedelta(hours=1)


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

        if not json_data or json_data.get("token") is None:
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
        if response is dict:
            response.update(execution_time_params)
        elif response is tuple:
            response = response[0].update(execution_time_params), *response[1:]
        return response

    wrapper.__name__ = f.__name__
    return wrapper


# async def index():
#     await collect_data()
#     main_isw_preparation()
#     main_isw_modeling()
#     main_alarm_modeling()
#     main_merge()
#     main_separate_data()
#     train_models()
#     tune_models()


def update_forecast():
    global last_prediction_time
    prediction_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    # yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    #
    # report_path = asyncio.run(get_report_for_date(yesterday))  # collect_data
    # csv_path = prepare_report(report_path)  # isw_preparation
    # isw_data_csv_path = process_file_data(csv_path)  # isw_modeling
    # weather_forecast = get_weather_forecast(WEATHER_API_KEY)  # get_weather
    # weather_csv_path = save_weather_to_csv(weather_forecast)  # save weather
    # df = merge_weather_alarm_keywords_for_files(weather_csv_path, ALARMS_DATA_FILE, isw_data_csv_path,
    #                                             yesterday)  # merge

    # set index and drop is_alarm
    # df['datetimeEpoch'] = df['hour_datetimeEpoch']
    # df.set_index('datetimeEpoch', inplace=True)
    # df = df.drop(labels=['is_alarm'], axis=1)

    # # update prediction
    if datetime.datetime.now() > last_prediction_time + datetime.timedelta(hours=1):
        last_prediction_time = prediction_time
        data = update_prediction_for_next_12_hours()
        data_vals = data.values.tolist()
        # save prediction
        save_predictions(data_vals, prediction_time)
        return {'status': 'OK'}
    return {'status': 'UP TO DATE'}


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
    return update_forecast()


@app.route(
    '/content/api/v1/integration/forecast/alarms',
    methods=["POST"],
)
@authorize_and_validate_request
@add_execution_time_params_to_response
def get_forecast_endpoint():
    regions = request.json['regions'] if 'regions' in request.json else []
    try:
        # if last_prediction_time == datetime.datetime.min:
        #     return
        predictions = get_predictions(last_prediction_time, regions)
        result = {
            "last_model_train_time": "2023-02-01T13:15:30Z",  # time when model was retrained last time
            "last_prediciotn_time": "2023-04-01T13:15:30Z",  # time when the prediction was updated
            "regions_forecast": predictions
        }
        return result
    except FileNotFoundError:
        return {"Error": "You must update the prediction first. /content/api/v1/integration/forecast/update"}, 400


if __name__ == '__main__':
    app.run(debug=True)