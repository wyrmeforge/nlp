from isw_data_modeling import main as main_isw_modeling
from alarm_data_modeling import main as main_alarm_modeling
from data_collectors.isw_data_collector import collect_data
from isw_data_preparation import main as main_isw_preparation
from merge import main as main_merge
from separate_test_data import main as main_separate_data
from train_model import train_models
from tune_model import tune_models
import asyncio


async def index():
    await collect_data()
    main_isw_preparation()
    main_isw_modeling()
    main_alarm_modeling()
    main_merge()
    main_separate_data()
    train_models()
    tune_models()


if __name__ == "__main__":
    asyncio.run(index())
