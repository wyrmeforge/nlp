import datetime
import os
import pickle
from datetime import date, timedelta

import pandas as pd

from storage import save_predictions


# REGIONS={'Chernivtsi': '1', 'Lutsk': '2', 'Vinnytsia': '3', 'Dnipro': '4', 'Donetsk': '5',
#            'Zhytomir': '6', 'Uzhgorod': '7', 'Zaporozhye': '8', 'Kyiv': '9',
#            'Kropyvnytskyi': '10', 'Lviv': '12', 'Mykolaiv': '13', 'Odesa': '14',
#            'Poltava': '15', 'Rivne': '16', 'Sumy': '17', 'Ternopil': '18', 'Kharkiv': '19',
#            'Kherson': '20', 'Khmelnytskyi': '21', 'Cherkasy': '22', 'Chernihiv':'23',
#            'Ivano-Frankivsk': '24'}


def get_prediction_data_for_12_hours(api_key, regions):
    row0 = get_last_words()
    rowdict = row0[19::]

    yesterday = date.today() - timedelta(days=1)
    from_date = datetime.date(yesterday.year, yesterday.month, yesterday.day)
    till_date = datetime.date(yesterday.year, yesterday.month, yesterday.day)

    isw_news = get_isw_news_for_date(from_date, till_date)

    not_in = {v: 0 for v in rowdict if v not in isw_news['news'].apply(pd.Series)}
    not_in = pd.Series([not_in])
    not_in = not_in.apply(pd.Series)

    series = isw_news['news'].apply(pd.Series)
    series = series.loc[:, series.columns.isin(rowdict)]
    series = pd.concat([series, not_in], axis=1)
    isw_news = pd.concat([isw_news.drop(['news', 'date'], axis=1), series], axis=1)

    isw_news['key_merge'] = 1

    res = []
    for region_name, region_id in regions.items():
        forecast = pd.DataFrame(get_weather(api_key, region_name + ',Ukraine'))
        forecast['key_merge'] = 1

        data = pd.merge(forecast, isw_news, on='key_merge').drop("key_merge", 1)
        data['region_id'] = region_id
        res.append(data)

    res = pd.concat(res)
    order = [r for r in row0 if r in res.columns]
    res = res[order]
    return res


now = datetime.datetime.now()
rounded_hour = (now.replace(second=0, microsecond=0, minute=0, hour=now.hour)
                + datetime.timedelta(hours=1))
print(rounded_hour)

LAST_MODEL_FILE = r'data/model/logistic_regression_model.pkl'


def update_prediction_for_next_12_hours():
    regions_reverse = {v: k for k, v in REGIONS.items()}
    with open(LAST_MODEL_FILE, 'rb') as f:
        model = pickle.load(f)
    data = get_prediction_data_for_12_hours(os.environ.get("WEATHER_API_KEY"), REGIONS)
    data = data.apply(pd.to_numeric, errors='coerce')
    data.fillna(0, inplace=True)
    pred = model.predict(data)
    data['is_alarm'] = pred
    data = data[['region_id', 'day_datetimeEpoch', 'is_alarm']]
    data['region_id'] = data['region_id'].apply(lambda x: regions_reverse[str(int(x))])
    data["day_datetimeEpoch"] = data["day_datetimeEpoch"].apply(lambda x: datetime.fromtimestamp(x))
    return data


def main():
    data = update_prediction_for_next_12_hours()
    data_vals = data.values.tolist()
    save_predictions(data_vals)


if __name__ == "__main__":
    # main()
    get_weather('V458GWVU2E6EVKWC2YUEJ8Y2T')
