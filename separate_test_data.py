import datetime
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit


FILE_PATH = 'data/output/all_merged_data2.csv'
RESULT_DIR = 'data/dataset'


def split(path):
    df = pd.read_csv(path, sep=';')

    df['datetimeEpoch'] = pd.to_datetime(df['day_datetime'] + ' ' + df['hour_datetime'])
    df['datetimeEpoch'] = (df.datetimeEpoch - datetime.datetime(1970, 1, 1)).dt.total_seconds().astype(int)
    df.set_index('datetimeEpoch', inplace=True)

    train: pd.DataFrame
    test: pd.DataFrame
    tss = TimeSeriesSplit(n_splits=4)
    for train_index, test_index in tss.split(df):
        train, test = df.iloc[train_index, :], df.iloc[test_index, :]
    x_train = train.drop(labels=['is_alarm'], axis=1)
    x_test = test.drop(labels=['is_alarm'], axis=1)
    y_train = train['is_alarm']
    y_test = test['is_alarm']

    x_train.to_csv(f'{RESULT_DIR}/x_train.csv', sep=';')
    x_test.to_csv(f'{RESULT_DIR}/x_test.csv', sep=';')
    y_train.to_csv(f'{RESULT_DIR}/y_train.csv', sep=';')
    y_test.to_csv(f'{RESULT_DIR}/y_test.csv', sep=';')


def main():
    split(FILE_PATH)


if __name__ == '__main__':
    main()
