from data_collectors.isw_data_collector import collect_data
from data_collectors.weather_data_collector import get_weather
from isw_data_preparation import main as main_preparation
from isw_data_modeling import main as main_data_modeling
from alarm_data_modeling import main as main_alarm_modeling
from train_model import train_models
from tune_model import tune_models

import asyncio
import os


async def init_app():
    await collect_data()
    await main_preparation()
    main_data_modeling()
    await get_weather()
    await main_alarm_modeling()
    os.system('python merge.py')
    os.system('python separate_test_data.py')
    train_models()
    tune_models()


async def main():
    await init_app()


if __name__ == '__main__':
    asyncio.run(main())
