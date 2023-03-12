
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from num2words import num2words
import glob
import numpy as np
import re

INPUT_DATA_FOLDER = "data"
OUTPUT_FOLDER = "datasets"
OUTPUT_DATA_FILE = "isw_reports.csv"
files_by_days = glob.glob(f"{INPUT_DATA_FOLDER}/*.txt")


def remove_one_letter_word(data):
    words = word_tokenize(str(data))

    new_tokens = []
    for token in words:
        if len(token) > 1:
            new_tokens.append(token)

    new_text = " ".join(new_tokens)
    return new_text


def convert_to_lower_case(data):
    return np.char.lower(data)


def remove_stop_words(data):
    stop_words = set(stopwords.words('english'))
    stop_words -= {"no", "not"}  # Remove "no" and "not" from the stop words list.

    words = word_tokenize(str(data))

    new_tokens = []
    for token in words:
        if token not in stop_words and len(token) > 1:
            new_tokens.append(token)

    new_text = " ".join(new_tokens)
    return new_text


def remove_punctuation(data):
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_—-~'''

    for i in range(len(punctuation)):
        data = np.char.replace(data, punctuation[i], ' ')
        data = np.char.replace(data, '  ', ' ')

    return data


def stemming(data):
    stemmer = PorterStemmer()

    tokens = word_tokenize(str(data))
    new_tokens = [stemmer.stem(token) for token in tokens]

    new_text = " ".join(new_tokens)
    return new_text


def lemmatizing(data):
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(str(data))
    new_tokens = [lemmatizer.lemmatize(token) for token in tokens]

    new_text = " ".join(new_tokens)
    return new_text


def convert_number(data):
    tokens = word_tokenize(str(data))

    new_tokens = []

    for token in tokens:
        if token.isdigit():
            if re.match(r'^\d+(st|nd|rd|th)$', token):
                new_token = num2words(token)
            elif int(token) < 100000000:
                new_token = num2words(token)
            else:
                new_token = ""
        else:
            new_token = token
        new_tokens.append(new_token)

    new_text = " ".join(new_tokens)
    new_text = np.char.replace(new_text, "-", " ")

    return new_text


def remove_url(data):
    tokens = word_tokenize(str(data))

    new_tokens = []
    for token in tokens:
        new_token = re.sub(r'https?://\S+', '', token)
        new_tokens.append(new_token)

    return " ".join(new_tokens)


def preprocess(data, alg="lemm"):
    data = remove_one_letter_word(data)
    data = remove_url(data)
    data = convert_to_lower_case(data)
    data = remove_punctuation(data)
    data = remove_stop_words(data)
    data = convert_number(data)
    data = stemming(data)

    if alg == "lemm":
        data = lemmatizing(data)
    else:
        data = stemming(data)

    data = remove_punctuation(data)
    data = remove_stop_words(data)

    return data


all_data = []

for file in files_by_days:
    dist = {}

    start_index = file.index('\\') + 1
    end_index = file.index('.txt')
    date = file[start_index:end_index]

    with open(file, "r", encoding='utf-8') as cfile:
        main_text = cfile.read()

        dist = {
            "date": date,
            "text": main_text,
        }

        all_data.append(dist)

df = pd.DataFrame.from_dict(all_data)
df = df.sort_values(by=['date'])

df['lemming'] = df['text'].apply(lambda x: preprocess(x, "lemm"))
df['stemming'] = df['text'].apply(lambda x: preprocess(x, "stem"))

df.to_csv(f"{OUTPUT_FOLDER}/{OUTPUT_DATA_FILE}", sep=";", index=False)
