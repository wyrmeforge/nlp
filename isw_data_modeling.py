import pickle

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from utils.tf_idf import convert_doc_to_keywords


INPUT_DATASET_FOLDER = "datasets"
DATA_FILE = "isw_reports.csv"
OUTPUT_FOLDER = "datasets"
OUTPUT_DATA_FILE = "isw_reports_v2.csv"


def load_data():
    df = pd.read_csv(f"{INPUT_DATASET_FOLDER}/{DATA_FILE}", sep=";")
    return df


def save_vectorizers(cv, tfidf_transformer):
    with open("model/count_vectorizer.pkl", "wb") as handle:
        pickle.dump(cv, handle)
    with open("model/tfidf_transformer.pkl", "wb") as handle:
        pickle.dump(tfidf_transformer, handle)


def load_vectorizers():
    tfidf = pickle.load(open("model/tfidf_transformer.pkl", "rb"))
    cv = pickle.load(open("model/count_vectorizer.pkl", "rb"))
    return cv, tfidf


def process_data():
    df = load_data()
    docs = df['lemming'].tolist()
    cv = CountVectorizer(max_df=0.98, min_df=2)
    word_counter_vector = cv.fit_transform(docs)
    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(word_counter_vector)
    save_vectorizers(cv, tfidf_transformer)
    cv, tfidf = load_vectorizers()
    df["keywords"] = df["lemming"].apply(lambda x: convert_doc_to_keywords(x, cv, tfidf))
    return df


def save_data(df):
    df.to_csv(f"{OUTPUT_FOLDER}/{OUTPUT_DATA_FILE}", sep=";", index=False)


def main():
    df = process_data()
    save_data(df)


if __name__ == '__main__':
    main()
