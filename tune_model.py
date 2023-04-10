from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import GridSearchCV
from sklearn import tree
from train_model import prepare_data, save_model, calculate_confusion
import pandas as pd

INPUT_DATA_FOLDER = "data/dataset"


def run_naive_bayes_model(X_train, X_test, y_train, y_test):
    print('Running Naive Bayes...')
    var_smoothing = [1e-10, 1e-9, 1e-8]
    param_grid = {'var_smoothing': var_smoothing}

    model = GaussianNB()
    cv = RepeatedKFold(n_splits=5, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1,
                               cv=cv, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    score = best_model.score(X_test, y_test)

    print(f"Naive Bayes accuracy score: {score:.4f}")
    return best_model


def run_logistic_regression(X_train, X_test, y_train, y_test):
    print('Running Logistic Regression...')
    param_grid = {
        'solver': ['lbfgs', 'liblinear'],
        'tol': [1e-3, 1e-4],
        'C': [1, 1.5]
    }

    model = LogisticRegression()
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1,
                               cv=cv, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    score = best_model.score(X_test, y_test)

    print(f"Logistic regression score: {score:.4f}")
    return best_model


def run_decision_tree_classifier_model(X_train, X_test, y_train, y_test):
    print('Running Decision Tree Classifier...')

    param_grid = {
        'criterion': ['gini', 'entropy'],
        'splitter': ['best', 'random'],
        'max_features': ['sqrt', 'log2']
    }

    model = tree.DecisionTreeClassifier()
    cv = RepeatedKFold(n_splits=5, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1,
                               cv=cv, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    score = best_model.score(X_test, y_test)

    print(f"Decision Tree Classifier score: {score:.4f}")
    return best_model


def tune_models():
    models = {
        'nv_model': run_naive_bayes_model,
        'lg_model': run_logistic_regression,
        'dtc_model': run_decision_tree_classifier_model,
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
        save_model(model, model_name + '_tuned')
        calculate_confusion(model_name + '_tuned', X_test, y_test)
        print('--------------------------')


if __name__ == "__main__":
    tune_models()
