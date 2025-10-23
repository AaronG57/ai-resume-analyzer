# utils/job_matcher.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def normalize_text(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def compute_match_score(resume_text, jd_text):
    """
    Returns a score in [0,100] representing similarity between resume and job description.
    Uses TF-IDF + cosine similarity on the whole texts, plus a skill keyword overlap boost.
    """
    resume_text = normalize_text(resume_text)
    jd_text = normalize_text(jd_text)
    texts = [resume_text, jd_text]

    vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words='english', max_features=4000)
    tfidf = vectorizer.fit_transform(texts)
    cos = cosine_similarity(tfidf[0], tfidf[1])[0][0]  # between 0 and 1

    # simple keyword overlap: extract likely "skills" by splitting jd by commas and common words
    jd_words = set([w for w in re.findall(r'\b[a-z0-9]+\b', jd_text) if len(w) > 2])
    resume_words = set([w for w in re.findall(r'\b[a-z0-9]+\b', resume_text) if len(w) > 2])
    overlap = len(jd_words & resume_words) / max(1, len(jd_words))

    # combine signals: weighting alpha for cos, beta for overlap
    alpha = 0.7
    beta = 0.3
    combined = alpha * cos + beta * overlap
    score = float(np.clip(combined * 100.0, 0, 100))
    return round(score, 1)
