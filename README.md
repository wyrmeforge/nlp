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

### Instructions

Follow these instructions:

1. Type `mkdir data` in your terminal to create a new directory named "data".
2. Type `python parser.py ; nlp.py ; tfidf.py` in your terminal to run the three Python scripts in sequence.

### Installation
```
pip install -r /path/to/requirements.txt
```
