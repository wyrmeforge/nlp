def convert_doc_to_keywords(doc, cv, tfidf):
    feature_names = cv.get_feature_names_out()
    tf_idf_vector = tfidf.transform(cv.transform([doc]))
    sorted_items = sort_coo(tf_idf_vector.tocoo())
    keywords = get_top_n_features(feature_names, sorted_items)
    return keywords
