import pandas as pd


REGIONS_FILE = r'data\0_raw_meta\regions.csv'


def get_regions():
    df_regions = pd.read_csv(REGIONS_FILE)
    return dict(df_regions[['region_id', 'center_city_en']].values)


if __name__ == '__main__':
    print(get_regions())
