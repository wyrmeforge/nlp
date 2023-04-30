import csv
from datetime import datetime


PATH_TO_PREDICTION_DATA = 'data/prediction/'
HEADER = ['region_name', 'datetime_epoch', 'is_alarm']


def save_predictions(predictions: list):
    with open(PATH_TO_PREDICTION_DATA, 'w', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(HEADER)
        for region_name, datetime_epoch, prediction in predictions:
            csv_writer.writerow((region_name, datetime_epoch, prediction))


def get_predictions(region_names: list = None):
    if region_names is None:
        region_names = []

    with open(PATH_TO_PREDICTION_DATA, encoding='utf-8') as f:
        reader = csv.reader(f)
        data = [row for row in reader if (region_names and row[0] in region_names) or not region_names][1:]

    data_dict: dict[str, dict] = dict.fromkeys(set([row[0] for row in data]), __value={})
    for row in data:
        data_dict[row[0]].update({row[1]: row[2]})

    return data_dict