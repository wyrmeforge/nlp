import codecs
import csv
import sys
import urllib.error
import urllib.request
from os import getenv


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


def main():
    get_weather()


if __name__ == '__main__':
    main()
