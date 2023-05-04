# Design and API Patterns Project

## Prediction alarm system
Prediction alarms system is an application for for predicting the probability of air alerts based on decision tree classifier and using data from news and weather forecasts

## Project Structure
```shell
├── data                       # Source files
├── data_collectors            # Web scraping code
├── ml                         # Predictions file fuctions
├── model                      # Models file
├── utils                      # Utility functions
├── ml                         # Predictions fuctions
├── alarm_data_modeling.py     # Data processing script
├── alarm_last_data.py         # Get alarms for last 12 hours script
├── app.py                     # Starting file
├── isw_data_modeling.py       # Text data processing script.
├── isw_data_preparation.py    # Text data preprocessing script.
├── merge.py                   # Data processing and merging.
├── requirements.txt           # File with requirenments
├── separate_rest_data.py      # Separate rest data script
├── train_model.py             # Training model script
├── tune_model.py              # Tune and evaluate classification models.
├── .gitignore                 # Git ignore file
├── README.md                  # Project README file
```

## Endpoints
### POST
`update prediction`  [/content/api/v1/integration/forecast/update](#post-update) <br/>
`do prediction`  [/content/api/v1/integration/forecast/alarms](#post-alarms) <br/>

### [POST] /content/api/v1/integration/forecast/update

The query updates predictions for next 12 hours.

**Response**
```
{
    "success": OK
}
```

if we do request less than hour ago
**Response**
```
{
    "success": UP TO DATE
}
```

**BODY Parameters**

|          Name | Required |  Type   | Description                                                                                                                                                         |
| -------------:|:--------:|:-------:| --------------------------------------------------------------------------------------------------------------------------|
|     `token` | required | string  | set token from the environments variable API_KEY                                                                   |

___

### [POST] /content/api/v1/integration/forecast/alarms

The query do predictions for regions for next 12 hours.

**Response**
```
{
    "last_model_train_time": "2023-02-01T13:15:30Z",
    "last_prediciotn_time": "2023-04-01T13:15:30Z",
    "regions_forecast": {
        "Kyiv": {
            "2023-05-05 00:00:00": "True",
            "2023-05-05 01:00:00": "False",
            "2023-05-05 02:00:00": "False",
            "2023-05-05 03:00:00": "False",
            "2023-05-05 04:00:00": "False",
            "2023-05-05 05:00:00": "False",
            "2023-05-05 06:00:00": "False",
            "2023-05-05 07:00:00": "False",
            "2023-05-05 08:00:00": "False",
            "2023-05-05 09:00:00": "False",
            "2023-05-05 10:00:00": "False"
        }
    }
}
```

If not found region

**Response**
```
{
    "last_model_train_time": "2023-02-01T13:15:30Z",
    "last_prediciotn_time": "2023-04-01T13:15:30Z",
    "regions_forecast": {}
}
```

If any implemented error

**Response**
```
{
    "code": 400,
    "Error": "You must update the prediction first. /content/api/v1/integration/forecast/update"
} 
```

**BODY Parameters**

|          Name | Required |  Type   | Description                                                                                                                                                         |
| -------------:|:--------:|:-------:| --------------------------------------------------------------------------------------------------------------------------|
|     `token` | required | string  | Token from the environments variable API_KEY                                                                   |
|     `regions` | required | string array  | Name of the alarm prediction regions                                                                  |

___

## Installation
```
pip install -r /path/to/requirements.txt
```
