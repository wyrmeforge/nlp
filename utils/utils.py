import pandas as pd


REGIONS_FILE = r'..\data\0_raw_meta\regions.csv'


def get_regions():
    df_regions = pd.read_csv(REGIONS_FILE)
    return df_regions ['center_city_en'].tolist()