import codecs
import csv
import datetime
import json
import sys
import urllib.error
import urllib.request
from os import getenv

import requests

from utils.utils import get_regions

OUTPUT_DATA_FOLDER = "data/output"
WEATHER_DATA_PREDICTION_FILE = "isw_reports_prepared.csv"


BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'


def get_weather():
    base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/'

    api_key = getenv("WEATHER_API_KEY")
    unit_group = 'us'
    location = 'kyiv'
    start_date = '2020-01-01'
    end_date = '2020-01-01'
    content_type = "csv"
    include = "days"
    api_query = base_url + location
    if len(start_date):
        api_query += "/" + start_date
        if len(end_date):
            api_query += "/" + end_date
    api_query += "?"
    if len(unit_group):
        api_query += "&unitGroup=" + unit_group

    if len(content_type):
        api_query += "&contentType=" + content_type

    if len(include):
        api_query += "&include=" + include

    api_query += "&key=" + api_key
    print(' - Running query URL: ', api_query)
    print()

    try:
        csv_bytes = urllib.request.urlopen(api_query)
    except urllib.error.HTTPError as e:
        error_info = e.read().decode()
        print('Error code: ', e.code, error_info)
        sys.exit()
    except  urllib.error.URLError as e:
        print(e)
        sys.exit()

    csv_text = csv.reader(codecs.iterdecode(csv_bytes, 'utf-8'))

    row_index = 0
    for row in csv_text:
        if row_index == 0:
            first_row = row
        else:
            print('Weather in ', row[0], ' on ', row[1])

            col_index = 0
            for _ in row:
                if col_index >= 4:
                    print('   ', first_row[col_index], ' = ', row[col_index])
                col_index += 1
        row_index += 1

    return csv_text


def get_weather_forecast(api_key, city='Kyiv'):
    def choose_day(hour: dict):
        return [
            day for day in days
            if datetime.datetime.fromtimestamp(day['datetimeEpoch']).date() ==
               datetime.datetime.fromtimestamp(hour['datetimeEpoch']).date()
        ][0]

    url = f'{BASE_URL}/{city}/{(datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")}/{(datetime.datetime.now() + datetime.timedelta(hours=15)).strftime("%Y-%m-%dT%H:%M:%S")}'
    params = {
        'unitGroup': 'metric',
        'key': f'{api_key}',
        'include': 'hours',
        'aggregateHours': '1',
        'hoursAhead': '12'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        curr_hour = (datetime.datetime.now() + datetime.timedelta(hours=1)).hour

        response = response.json()
        days = [day for day in response['days']]
        hours = days[0]['hours'][curr_hour:]
        if len(days) > 1:
            hours += days[1]['hours']

        hourly_forecast = [
            {
                'city_resolvedAddress': response['resolvedAddress'],
                'day_datetime': hour['datetime'],
                'day_datetimeEpoch': hour['datetimeEpoch'],
                'day_tempmax': choose_day(hour)['tempmax'],
                'day_tempmin': choose_day(hour)['tempmin'],
                'day_temp': choose_day(hour)['temp'],
                'day_dew': choose_day(hour)['dew'],
                'day_humidity': choose_day(hour)['humidity'],
                'day_precip': choose_day(hour)['precip'],
                'day_precipcover': choose_day(hour)['precipcover'],
                'day_solarradiation': choose_day(hour)['solarradiation'],
                'day_solarenergy': choose_day(hour)['solarenergy'],
                'day_uvindex': choose_day(hour)['uvindex'],
                'day_sunrise': choose_day(hour)['sunrise'],
                'day_sunset': choose_day(hour)['sunset'],
                'day_moonphase': choose_day(hour)['moonphase'],
                'hour_datetime': hour['datetime'],
                'hour_datetimeEpoch': hour['datetimeEpoch'],
                'hour_temp': hour['temp'],
                'hour_humidity': hour['humidity'],
                'hour_dew': hour['dew'],
                'hour_precip': hour['precip'],
                'hour_precipprob': hour['precipprob'],
                'hour_snow': hour.get('snow', 0),
                'hour_snowdepth': hour.get('snowdepth', 0),
                'hour_preciptype': hour['preciptype'],
                'hour_windgust': hour['windgust'],
                'hour_windspeed': hour['windspeed'],
                'hour_winddir': hour['winddir'],
                'hour_pressure': hour['pressure'],
                'hour_visibility': hour['visibility'],
                'hour_cloudcover': hour['cloudcover'],
                'hour_solarradiation': hour['solarradiation'],
                'hour_solarenergy': hour['solarenergy'],
                'hour_uvindex': hour['uvindex'],
                'hour_severerisk': hour['severerisk'],
                'hour_conditions': hour['conditions']
            }
            for hour in hours[:12]
        ]
        return hourly_forecast
    else:
        return ('Error:', response.status_code, response.text)


def main():
    # get_weather()
    weather = get_weather_forecast(getenv('WEATHER_API_KEY'))
    with open('result_weather.json', 'w', encoding='utf-8') as f:
        json.dump(weather, f)


if __name__ == '__main__':
    main()
