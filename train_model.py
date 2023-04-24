import pandas as pd
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
import time
import pickle
from sklearn.metrics import confusion_matrix

INPUT_DATA_FOLDER = "data/dataset"
MODEL_FOLDER = "model"

FEATURES_TO_INCLUDE = [
    'city_resolvedAddress',
    'event_start',
    'event_end',
    'hour_windspeed',
    'hour_conditions',
    'day_humidity',
    'hour_snow',
    'hour_pressure',
    'hour_visibility',
    'hour_precip',
    'hour_windgust',
    'hour_cloudcover',
    'hour_severerisk',
    'day_temp',
]


def calculate_confusion(filename, X_test, y_test):
    with open(f"{MODEL_FOLDER}/{filename}.pkl", 'rb') as f:
        model = pickle.load(f)

    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    print(f'Confusion Matrix:')
    print(cm)


def save_model(model, filename):
    with open(f"{MODEL_FOLDER}/{filename}.pkl", 'wb') as f:
        pickle.dump(model, f)


def prepare_data(x, y):
    X = x[FEATURES_TO_INCLUDE]
    y = y['is_alarm']

    # Convert all columns to float
    X = X.apply(pd.to_numeric, errors='coerce')
    y = y.apply(pd.to_numeric, errors='coerce')

    # Replace NaN values with default
    X.fillna(0, inplace=True)
    y.fillna(0, inplace=True)

    return X, y


def run_logistic_regression(X_train, X_test, y_train, y_test):
    print('Running Logistic Regression...')

    start_time = time.time()

    model = LogisticRegression()

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    processing_time = time.time() - start_time

    print(f"Score: {score}. Processing time {processing_time:.2f} seconds")

    return model


def run_svc_model(X_train, X_test, y_train, y_test):
    print('Running SVC...')

    start_time = time.time()

    model = SVC()

    model.fit(X_train, y_train)
    print(f"Fit time {time.time() - start_time} seconds")
    score = model.score(X_test, y_test)

    processing_time = time.time() - start_time

    print(f"Score: {score}. Processing time {processing_time:.2f} seconds")

    return model


def run_sgd_model(X_train, X_test, y_train, y_test):
    print('Running SGD...')

    start_time = time.time()

    model = SGDClassifier(max_iter=1000, tol=1e-3, penalty="elasticnet")

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    processing_time = time.time() - start_time

    print(f"Score: {score}. Processing time {processing_time:.2f} seconds")

    return model


def run_random_forest_model(X_train, X_test, y_train, y_test):
    print('Running Random Forest...')

    start_time = time.time()

    model = RandomForestClassifier(n_estimators=100, max_depth=None, random_state=42)

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    processing_time = time.time() - start_time

    print(f"Score: {score}. Processing time {processing_time:.2f} seconds")

    return model


def run_naive_bayes_model(X_train, X_test, y_train, y_test):
    print('Running Naive Bayes...')

    start_time = time.time()
    model = GaussianNB()

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    processing_time = time.time() - start_time

    print(f"Score: {score}. Processing time {processing_time:.2f} seconds")

    return model


def run_decision_tree_classifier_model(X_train, X_test, y_train, y_test):
    print('Running Decision tree classifier...')

    start_time = time.time()

    model = tree.DecisionTreeClassifier()

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    processing_time = time.time() - start_time

    print(f"Score: {score}. Processing time {processing_time:.2f} seconds")

    return model


def train_models():
    models = {
        'lg_model': run_logistic_regression,
        'sgd_model': run_sgd_model,
        'random_forest_model': run_random_forest_model,
        'nv_model': run_naive_bayes_model,
        'dtc_model': run_decision_tree_classifier_model,
        'svc_model': run_svc_model
    }

    X_train = pd.read_csv(f'{INPUT_DATA_FOLDER}/x_train.csv', sep=';')
    X_test = pd.read_csv(f'{INPUT_DATA_FOLDER}/x_test.csv', sep=';')
    y_train = pd.read_csv(f'{INPUT_DATA_FOLDER}/y_train.csv', sep=';')
    y_test = pd.read_csv(f'{INPUT_DATA_FOLDER}/y_test.csv', sep=';')

    X_train, y_test = prepare_data(X_train, y_test)
    X_test, y_train = prepare_data(X_test, y_train)

    for model_name, model_func in models.items():
        print('--------------------------')
        model = model_func(X_train, X_test, y_train, y_test)
        print(f"Predict {model.predict(X_train)}")
        print("Save model...")
        save_model(model, model_name)
        calculate_confusion(model_name, X_test, y_test)
        print('--------------------------')


if __name__ == "__main__":
    train_models()
