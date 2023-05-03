import asyncio
import datetime
import os
import pickle

import pandas as pd

from alarms_last_data import get_alarms_for_last_12_H
from data_collectors.isw_data_collector import get_report_for_date
from data_collectors.weather_data_collector import get_weather_forecast, save_all_weather_data_to_csv
from isw_data_modeling import process_file_data
from isw_data_preparation import prepare_report
from merge import merge_weather_alarm_keywords_for_files, ALARMS_DATA_FILE
from ml.storage import save_predictions
from train_model import FEATURES_TO_INCLUDE
from utils.utils import get_regions


# from storage import save_predictions


# REGIONS={'Chernivtsi': '1', 'Lutsk': '2', 'Vinnytsia': '3', 'Dnipro': '4', 'Donetsk': '5',
#            'Zhytomir': '6', 'Uzhgorod': '7', 'Zaporozhye': '8', 'Kyiv': '9',
#            'Kropyvnytskyi': '10', 'Lviv': '12', 'Mykolaiv': '13', 'Odesa': '14',
#            'Poltava': '15', 'Rivne': '16', 'Sumy': '17', 'Ternopil': '18', 'Kharkiv': '19',
#            'Kherson': '20', 'Khmelnytskyi': '21', 'Cherkasy': '22', 'Chernihiv':'23',
#            'Ivano-Frankivsk': '24'}


def get_prediction_data_for_12_hours(api_key):
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

    report_path = asyncio.run(get_report_for_date(yesterday))  # collect_data
    csv_path = prepare_report(report_path)  # isw_preparation
    isw_data_csv_path = process_file_data(csv_path)  # isw_modeling
    # isw_news = pd.read_csv(isw_data_csv_path, sep=";")

    # weather_forecast = get_weather_forecast(api_key)  # get_weather
    # weather_csv_path = save_weather_to_csv(weather_forecast)  # save weather
    # df = merge_weather_alarm_keywords_for_files(weather_csv_path, ALARMS_DATA_FILE, isw_data_csv_path,
    #                                             yesterday)  # merge
    # isw_news['key_merge'] = 1

    res = []
    for region_id, region_name in get_regions().items():
        forecast = pd.DataFrame(get_weather_forecast(api_key, region_name + ',Ukraine'))
        # forecast['key_merge'] = 1

        # data = pd.merge(forecast, isw_news, on='key_merge').drop("key_merge", 1)
        # data['region_id'] = region_id
        # res.append(data)
        res.append(forecast)

    all_weather = pd.concat(res)
    weather_csv_path = save_all_weather_data_to_csv(all_weather)

    # weather - forecast for the next 12 hours
    # TODO alarms - alarms data for the PREVIOUS 12 hours
    # isw - the LAST isw report (yesterday, or the day before yesterday)
    get_alarms_for_last_12_H()

    res = merge_weather_alarm_keywords_for_files(weather_csv_path, ALARMS_DATA_FILE, isw_data_csv_path,
                                                 yesterday + datetime.timedelta(days=1))  # merge

    return res


now = datetime.datetime.now()
rounded_hour = (now.replace(second=0, microsecond=0, minute=0, hour=now.hour)
                + datetime.timedelta(hours=1))
print(rounded_hour)

LAST_MODEL_FILE = r'data/model/dtc_model.pkl'


def update_prediction_for_next_12_hours():
    regions = get_regions()
    with open(LAST_MODEL_FILE, 'rb') as f:
        model = pickle.load(f)

    data = get_prediction_data_for_12_hours(os.environ.get("WEATHER_API_KEY"))
    data['datetimeEpoch'] = data['hour_datetimeEpoch']
    data.set_index('datetimeEpoch', inplace=True)

    data = data.drop(labels=['is_alarm'], axis=1)
    data = data.apply(pd.to_numeric, errors='coerce')
    data.fillna(0, inplace=True)

    data = data[FEATURES_TO_INCLUDE]
    pred = model.predict(data)

    data['is_alarm'] = pred
    data = data[['region_id', 'is_alarm']]
    data['region_id'] = data['region_id'].apply(lambda x: regions[int(x)])
    data["datetimeEpoch"] = data.index.to_series().apply(lambda x: datetime.datetime.fromtimestamp(x))
    return data


def main():
    data = update_prediction_for_next_12_hours()
    data_vals = data.values.tolist()
    save_predictions(data_vals)


if __name__ == "__main__":
    main()
