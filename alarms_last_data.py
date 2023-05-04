from os import getenv

import requests
import csv
from datetime import datetime, timedelta
import pandas as pd

API_KEY = getenv('ALARMS_API_KEY')

# we don`t have 16 because it Luhansk
region_id_alarms = {'Khmelnytskyi': '3',
                    'Vinnytsia': '4',
                    'Rivne': '5',
                    'Lutsk': '8',
                    'Dnipro': '9',
                    'Zhytomyr': '10',
                    'Uzhgorod': '11',
                    'Zaporozhye': '12',
                    'Ivano-Frankivsk': '13',
                    'Kyiv': '14',
                    'Kropyvnytskyi': '15',
                    'Mykolaiv': '17',
                    'Odesa': '18',
                    'Poltava': '19',
                    'Sumy': '20',
                    'Ternopil': '21',
                    'Kharkiv': '22',
                    'Kherson': '23',
                    'Cherkasy': '24',
                    'Chernihiv': '25',
                    'Chernivtsi': '26',
                    'Lviv': '27',
                    'Donetsk': '28',
                    }


def last_alarms(region_id):
    url = 'https://api.ukrainealarm.com/api/v3/alerts/regionHistory'
    params = {'regionId': region_id}
    headers = {
        'accept': 'application/json',
        'Authorization': f'{API_KEY}'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data[0]['alarms']
    else:
        return response.status_code


def is_newer_than_12_hours(startDate):
    now = datetime.now()
    now = now.replace(second=0, microsecond=0, minute=0, hour=now.hour) + timedelta(hours=1)
    startDate = datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=12)
    return now <= startDate


# id
# region_id
# region_title
# region_city
# all_region
# start
# end
# clean_end
# intersection_alarm_id


def build_correct_alarm(alarm, id):
    region_id = alarm['region_id']  # | region_id
    region_title = alarm['region_title']  # | region_title
    region_city = alarm['region_title']  # | region_city
    start = alarm['startDate']  # | start
    end = alarm['endDate']  # | end
    clean_end = alarm['endDate']  # | clean_end
    if alarm['isContinue']:
        end = alarm['startDate']  # | end
        clean_end = alarm['startDate']  # | clean_end
    intersection_alarm_id = 'NULL'  # | intersection_alarm_id
    return [id, region_id, region_title, region_city, 1, start, end, clean_end, intersection_alarm_id]


def write_to_csv(data):
    # Make data frame of above data
    df = pd.DataFrame(data)
    # append data frame to CSV file
    df.to_csv('alarms_12_hours.csv', mode='a', index=False, header=False)


def get_alarms_for_last_12_H():
    alarms_12H = []
    for region in region_id_alarms:
        region_id = region_id_alarms[region]
        for alarm in last_alarms(region_id):
            startDate = alarm['startDate']
            if is_newer_than_12_hours(startDate):
                alarm['region_id'] = region_id
                alarm['region_title'] = region
                alarms_12H.append(alarm)

    header = ["id", "region_id", "region_title", "region_city", "all_region", "start", "end", "clean_end",
              "intersection_alarm_id"]

    filename = 'alarm_' + datetime.now().strftime("%Y-%m-%d") + '.csv'
    with open(f'data/output/{filename}', mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(header)
        id = 1
        for alarm in alarms_12H:
            writer.writerow(build_correct_alarm(alarm, id))
            id += 1


# if __name__ == "__main__":
#     get_alarms_for_last_12_H()
