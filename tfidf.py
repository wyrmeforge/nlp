import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

INPUT_DATASET_FOLDER = "datasets"
DATA_FILE = "isw_reports.csv"
OUTPUT_FOLDER = "datasets"
OUTPUT_DATA_FILE = "isw_reports.csv"


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


def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)


def get_top_n_features(feature_names, sorted_items, topn=10):
    sorted_items = sorted_items[:topn]
    score_vals = []
    feature_vals = []
    for idx, score in sorted_items:
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])
    results = {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]] = score_vals[idx]
    return results


def convert_doc_to_keywords(doc, cv, tfidf):
    feature_names = cv.get_feature_names_out()
    tf_idf_vector = tfidf.transform(cv.transform([doc]))
    sorted_items = sort_coo(tf_idf_vector.tocoo())
    keywords = get_top_n_features(feature_names, sorted_items)
    return keywords


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


if __name__ == '__main__':
    df = process_data()
    save_data(df)
