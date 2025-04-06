from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(jd_text, num_keywords=10):
    """Extracts the most important keywords from a job description using TF-IDF."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([jd_text])
    
    feature_array = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray().flatten()

    keywords = sorted(zip(feature_array, tfidf_scores), key=lambda x: x[1], reverse=True)
    return [word for word, score in keywords[:num_keywords]]
