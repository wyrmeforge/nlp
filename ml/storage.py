import csv
import datetime
from pathlib import Path


PATH_TO_PREDICTION_DATA = 'data/prediction/'
HEADER = ['region_name', 'datetime_epoch', 'is_alarm']


def get_path_to_prediction(prediction_time: datetime.datetime):
    return Path(PATH_TO_PREDICTION_DATA, f"{prediction_time.strftime('%Y-%m-%dT%H')}.csv")


def save_predictions(predictions: list, prediction_time: datetime.datetime):
    filepath = get_path_to_prediction(prediction_time)
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(HEADER)
        for region_name, datetime_epoch, prediction in predictions:
            csv_writer.writerow((region_name, datetime_epoch, prediction))


def get_predictions(prediction_time, region_names: list = None):
    if region_names is None:
        region_names = []

    with open(get_path_to_prediction(prediction_time), encoding='utf-8') as f:
        reader = csv.reader(f)
        data = [row for row in reader if (region_names and row[0] in region_names) or not region_names][1:]

    data_dict: dict[str, dict] = dict.fromkeys(set([row[0] for row in data]), {})
    for row in data:
        data_dict[row[0]].update({row[2]: row[1]})

    return data_dict
