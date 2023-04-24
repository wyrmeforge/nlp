# %%
import datetime
import numpy as np
import pandas as pd

# %%
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# %%
INPUT_DATA_ISW_FOLDER = "datasets"
INPUT_DATA_ALARM_FOLDER = "data/output"
INPUT_DATA_ALL_WEATHER_FOLDER = "data/0_raw_weather"
INPUT_REGIONS_DATA_FOLDER = "data/0_raw_meta"

ISW_DATA_FILE = "isw_reports_v2.csv"
ALARMS_DATA_FILE = "alarms.csv"
REGIONS_DATA_FILE = "regions.csv"
ALL_WEATHER_DATA_FILE = "all_weather_by_hour.csv"


OUTPUT_DATA_FOLDER = "data/output"
ISW_DATA_PREPARED_FILE = "isw_reports_prepared.csv"
ALARMS_WEATHER_MERGED_DATA_FILE = "alarms_weather_merged.csv"
ALL_MERGED_DATA_FILE = "all_merged_data.csv"



# %%
def isNaN(num):
    return num != num

# %%
df_isw = pd.read_csv(f"{INPUT_DATA_ISW_FOLDER}/{ISW_DATA_FILE}", sep=";")

# %%
df_isw.head(3)

# %%
df_isw = df_isw.drop(["text", "lemming", "stemming"], axis=1)

# %%
df_isw["date_datetime"] = pd.to_datetime(df_isw["date"])

# %%
df_isw['date_tomorrow_datetime'] = df_isw['date_datetime'].apply(lambda x: x+datetime.timedelta(days=1))

# %%
"""
## Prepare ISW
"""

# %%
df_isw = df_isw.rename(columns = {"date_datetime":"report_date"})
df_isw.to_csv(f"{OUTPUT_DATA_FOLDER}/{ISW_DATA_PREPARED_FILE}", sep=";", index=False)

# %%
df_isw.head(3)

# %%
"""
## Prepare alarms
"""

# %%
df_alarms = pd.read_csv(f"{INPUT_DATA_ALARM_FOLDER}/{ALARMS_DATA_FILE}", sep=";")

# %%
df_alarms_v2 = df_alarms.drop(["id","region_id"],axis=1)

# %%
df_alarms_v2.head(5)

# %%
df_alarms_v2["start_time"] = pd.to_datetime(df_alarms_v2["start"])
df_alarms_v2["end_time"] = pd.to_datetime(df_alarms_v2["end"])

# %%
df_alarms_v2["start_hour"] = df_alarms_v2['start_time'].dt.floor('H')
df_alarms_v2["end_hour"] = df_alarms_v2['end_time'].dt.ceil('H')

# %%
df_alarms_v2["start_hour"] = df_alarms_v2.apply(lambda x: x["start_hour"] if not isNaN(x["start_hour"]) else x["event_hour"] , axis=1)
df_alarms_v2["end_hour"] = df_alarms_v2.apply(lambda x: x["end_hour"] if not isNaN(x["end_hour"]) else x["event_hour"] , axis=1)

# %%
df_alarms_v2.head(5)

# %%
df_alarms_v2["day_date"] = df_alarms_v2["start_time"].dt.date

# %%
df_alarms_v2["start_hour_datetimeEpoch"] = df_alarms_v2['start_hour'].apply(lambda x: int(x.timestamp()) if not isNaN(x) else None)
df_alarms_v2["end_hour_datetimeEpoch"] = df_alarms_v2['end_hour'].apply(lambda x: int(x.timestamp()) if not isNaN(x) else None)

# %%
df_alarms_v2.head(5)

# %%
df_alarms_v2.shape

# %%
"""
## Prepare Weather
"""

# %%
df_weather = pd.read_csv(f"{INPUT_DATA_ALL_WEATHER_FOLDER}/{ALL_WEATHER_DATA_FILE}")
df_weather["day_datetime"] = pd.to_datetime(df_weather["day_datetime"])

# %%
df_weather.shape

# %%
df_weather.head(3)

# %%
# exclude
weather_exclude = [
"day_feelslikemax",
"day_feelslikemin",
"day_sunriseEpoch",
"day_sunsetEpoch",
"day_description",
"city_latitude",
"city_longitude",
"city_address",
"city_timezone",
"city_tzoffset",
"day_feelslike",
"day_precipprob",
"day_snow",
"day_snowdepth",
"day_windgust",
"day_windspeed",
"day_winddir",
"day_pressure",
"day_cloudcover",
"day_visibility",
"day_severerisk",
"day_conditions",
"day_icon",
"day_source",
"day_preciptype",
"day_stations",
"hour_icon",
"hour_source",
"hour_stations",
"hour_feelslike"
]

# %%
df_weather_v2 = df_weather.drop(weather_exclude, axis=1)

# %%
df_weather_v2["city"] = df_weather_v2["city_resolvedAddress"].apply(lambda x: x.split(",")[0])
df_weather_v2["city"] = df_weather_v2["city"].replace('Хмельницька область', "Хмельницький")

# %%
df_weather_v2.head(5)

# %%
df_weather_v2.shape

# %%
"""
## Merging Data
"""

# %%
df_regions = pd.read_csv(f"{INPUT_REGIONS_DATA_FOLDER}/{REGIONS_DATA_FILE}")

# %%
df_regions.head(5)

# %%
df_weather_reg = pd.merge(df_weather_v2, df_regions, left_on="city",right_on="center_city_ua")

# %%
df_weather_reg.head(10)

# %%
df_weather_reg.shape

# %%
df_weather_v2.shape

# %%
df_alarms_v2.dtypes

# %%
df_alarms_v2.head(3)

# %%
events_dict = df_alarms_v2.to_dict('records')
events_by_hour = []

# %%
events_dict[0]

# %%
for event in events_dict:
    for d in pd.date_range(start=event["start_hour"], end=event["end_hour"], freq='1H'):
        et = event.copy()
        et["hour_level_event_time"] = d
        events_by_hour.append(et)

# %%
df_events_v3 = pd.DataFrame.from_dict(events_by_hour)

# %%
df_events_v3["hour_level_event_datetimeEpoch"] = df_events_v3["hour_level_event_time"].apply(lambda x: int(x.timestamp()) if not isNaN(x) else None)

# %%
df_events_v3.shape

# %%
df_events_v3.head(15)

# %%
df_weather_reg.head(5)

# %%
df_weather_reg.shape

# %%
df_events_v4 = df_events_v3.copy().add_prefix('event_')

# %%
df_events_v4.head(5)

# %%
df_weather_v4 = df_weather_reg.merge(df_events_v4, 
                                     how="left", 
                                     left_on=["region_alt","hour_datetimeEpoch"],
                                     right_on=["event_region_title","event_hour_level_event_datetimeEpoch"])

# %%
df_weather_v4.to_csv(f"{OUTPUT_DATA_FOLDER}/{ALARMS_WEATHER_MERGED_DATA_FILE}", sep=";")

# %%
df_weather_v4.head(10)

# %%
df_weather_v4.shape

# %%
"""
## Merge Weather-Alarm-Keywords
"""

# %%
df_wak = df_weather_v4.merge(df_isw, how="left",
                             left_on=["day_datetime"],
                             right_on=["report_date"])

# %%
df_wak.shape

# %%
df_wak["is_alarm"] = df_wak["event_region_city"].notna()

# %%
df_wak.to_csv(
    f"{OUTPUT_DATA_FOLDER}/{ALL_MERGED_DATA_FILE}", sep=";", index=False)