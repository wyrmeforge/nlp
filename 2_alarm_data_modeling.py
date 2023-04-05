import pandas as pd


def read_data(input_folder, input_data):
    data = pd.read_csv(f"{input_folder}/{input_data}", sep=';')
    return data


def round_times(data):
    data['start_round'] = pd.to_datetime(data['start'])
    data['start_round'] = data['start_round'].dt.floor('H')
    data['end_round'] = pd.to_datetime(data['end'])
    data['end_round'] = data['end_round'].dt.floor('H')
    return data


def count_region_nums(data):
    # A number of regions where the alarm is going on;
    data['region_nums'] = 0
    groups = data.groupby(['start_round', 'end_round'])

    for name, group in groups:
        region_nums = len(group['region_id'].unique())
        data.loc[(data['start_round'] == name[0]) & (data['end_round'] == name[1]), 'region_nums'] = region_nums
    return data


def add_alarm_nums_last_24h(data):
    data['start'] = pd.to_datetime(data['start'])
    data['end'] = pd.to_datetime(data['end'])
    grouped = data.groupby(['region_id', pd.Grouper(key='start', freq='24H')])
    data['alarm_nums_24h'] = grouped['region_id'].transform('count').astype(float)
    return data


def save_data(output_folder, output_file, data):
    data.to_csv(f"{output_folder}/{output_file}", index=False, sep=';')


def drop_unnecessary_fields(data):
    return data.drop(["start_round", "end_round"], axis=1)

if __name__ == "__main__":
    INPUT_FOLDER = "data/input"
    INPUT_DATA = "alarms_origin.csv"
    OUTPUT_FOLDER = "data/output"
    OUTPUT_DATA = "alarms.csv"

    alarms = read_data(INPUT_FOLDER, INPUT_DATA)
    alarms = round_times(alarms)
    alarms = count_region_nums(alarms)
    alarms = add_alarm_nums_last_24h(alarms)
    alarms = drop_unnecessary_fields(alarms)
    save_data(OUTPUT_FOLDER, OUTPUT_DATA, alarms)