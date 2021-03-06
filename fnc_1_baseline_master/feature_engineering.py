import os
import re
import nltk
import numpy as np
from sklearn import feature_extraction
from fnc_1_baseline_master.LIWC.LIWCutil import parse_liwc, reverse_dict
from nltk.sentiment import SentimentIntensityAnalyzer
import math

_wnl = nltk.WordNetLemmatizer()
_sia = SentimentIntensityAnalyzer()

def normalize_word(w):
    return _wnl.lemmatize(w).lower() #_wnl.lemmatize(w.decode('utf-8')).lower()


def get_tokenized_lemmas(s):
    return [normalize_word(t) for t in nltk.word_tokenize(s)]


def clean(s):
    # Cleans a string: Lowercasing, trimming, removing non-alphanumeric

    return " ".join(re.findall(r'\w+', s, flags=re.UNICODE)).lower()


def remove_stopwords(l):
    # Removes stopwords from a list of tokens
    return [w for w in l if w not in feature_extraction.text.ENGLISH_STOP_WORDS]

def get_sentiment_difference(headlines, bodies):
    X = []
    for i in range(len(headlines)):
        h_sentiment = _sia.polarity_scores(headlines[i])
        b_sentiment = _sia.polarity_scores(" ".join(bodies[i]))
        x = [math.fabs(h_sentiment['compound'] - b_sentiment['compound']), math.fabs(h_sentiment['neu'] - b_sentiment['neu']), math.fabs(h_sentiment['pos'] - b_sentiment['pos']), math.fabs(h_sentiment['neg'] - b_sentiment['neg'])]
        X.append(x)
    return X

def get_tfidf(headlines, bodies):
    tfidf_vec = feature_extraction.text.TfidfVectorizer()
    tfidf_h = tfidf_vec.fit_transform(headlines)
    # Transform bodies to be one string instead list of words
    bodies_str = [" ".join(body) for body in bodies]
    print(str(bodies))
    tfidf_b = tfidf_vec.fit_transform(bodies_str)
    return tfidf_h, tfidf_b

def gen_feats(feat_fn, headlines, bodies, feature_file):
    feats = feat_fn(headlines, bodies)
    np.save(feature_file, feats)
    np.load(feature_file)

def gen_or_load_feats(feat_fn, headlines, bodies, feature_file):
    if not os.path.isfile(feature_file):
        feats = feat_fn(headlines, bodies)
        np.save(feature_file, feats)

    return np.load(feature_file)

def gen_or_load_feats_liwc(feat_fn, lexicon_list, headlines, bodies, feature_file):
    if not os.path.isfile(feature_file):
        feats = feat_fn(lexicon_list, headlines, bodies)
        np.save(feature_file, feats)

    return np.load(feature_file)


def word_overlap_features(headlines, bodies):
    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_body = clean(body)
        clean_headline = get_tokenized_lemmas(clean_headline)
        clean_body = get_tokenized_lemmas(clean_body)
        features = [
            len(set(clean_headline).intersection(clean_body)) / float(len(set(clean_headline).union(clean_body)))]
        X.append(features)
    return X


def refuting_features(headlines, bodies):
    _refuting_words = [
        'fake',
        'fraud',
        'hoax',
        'false',
        'deny', 'denies',
        # 'refute',
        'not',
        'despite',
        'nope',
        'doubt', 'doubts',
        'bogus',
        'debunk',
        'pranks',
        'retract'
    ]
    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_headline = get_tokenized_lemmas(clean_headline)
        features = [1 if word in clean_headline else 0 for word in _refuting_words]
        X.append(features)
    return X


def polarity_features(headlines, bodies):
    _refuting_words = [
        'fake',
        'fraud',
        'hoax',
        'false',
        'deny', 'denies',
        'not',
        'despite',
        'nope',
        'doubt', 'doubts',
        'bogus',
        'debunk',
        'pranks',
        'retract'
    ]

    def calculate_polarity(text):
        tokens = get_tokenized_lemmas(text)
        return sum([t in _refuting_words for t in tokens]) # % 2
    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_body = clean(body)
        features = []
        features.append(calculate_polarity(clean_headline))
        features.append(calculate_polarity(clean_body))
        X.append(features)
    return np.array(X)

def discuss_features(headlines, bodies):
    _discuss_words = ['according', 'maybe', 'reporting', 'reports', 'say', 'says', 'claim', 'claims', 'purportedly', 'investigating', 'told', 'tells', 'allegedly', 'validate', 'verify']

    def calculate_discuss(text):
        tokens = get_tokenized_lemmas(text)
        return sum([t in _discuss_words for t in tokens]) # % 2
    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_body = clean(body)
        features = []
        features.append(calculate_discuss(clean_headline))
        features.append(calculate_discuss(clean_body))
        X.append(features)
    return np.array(X)

# Returns dictionary of category = words we want
def LIWC_lexicons(w):
    d = parse_liwc(w)
    rev_d = reverse_dict(d)
    short_dict = {}
    short_dict['pronoun'] = rev_d['pronoun']
    short_dict['anger'] = rev_d['anger']
    short_dict['anx'] = rev_d['anx']
    short_dict['negate'] = rev_d['negate']
    short_dict['quant'] = rev_d['quant']
    return short_dict

def reg_counts(lexicon_list, headlines, bodies):
    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_headline = get_tokenized_lemmas(clean_headline)
        features = [1 if word in clean_headline else 0 for word in lexicon_list]
        X.append(features)
    return X

def overlap_counts(lexicon_list, headlines, bodies):

    def calculate_discuss(text):
        tokens = get_tokenized_lemmas(text)
        return sum([t in lexicon_list for t in tokens]) % 2
    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        clean_headline = clean(headline)
        clean_body = clean(body)
        features = []
        features.append(calculate_discuss(clean_headline))
        features.append(calculate_discuss(clean_body))
        X.append(features)
    return np.array(X)

def ngrams(input, n):
    input = input.split(' ')
    output = []
    for i in range(len(input) - n + 1):
        output.append(input[i:i + n])
    return output


def chargrams(input, n):
    output = []
    for i in range(len(input) - n + 1):
        output.append(input[i:i + n])
    return output


def append_chargrams(features, text_headline, text_body, size):
    grams = [' '.join(x) for x in chargrams(" ".join(remove_stopwords(text_headline.split())), size)]
    grams_hits = 0
    grams_early_hits = 0
    grams_first_hits = 0
    for gram in grams:
        if gram in text_body:
            grams_hits += 1
        if gram in text_body[:255]:
            grams_early_hits += 1
        if gram in text_body[:100]:
            grams_first_hits += 1
    features.append(grams_hits)
    features.append(grams_early_hits)
    features.append(grams_first_hits)
    return features


def append_ngrams(features, text_headline, text_body, size):
    grams = [' '.join(x) for x in ngrams(text_headline, size)]
    grams_hits = 0
    grams_early_hits = 0
    for gram in grams:
        if gram in text_body:
            grams_hits += 1
        if gram in text_body[:255]:
            grams_early_hits += 1
    features.append(grams_hits)
    features.append(grams_early_hits)
    return features


def hand_features(headlines, bodies):

    def binary_co_occurence(headline, body):
        # Count how many times a token in the title
        # appears in the body text.
        bin_count = 0
        bin_count_early = 0
        for headline_token in clean(headline).split(" "):
            if headline_token in clean(body):
                bin_count += 1
            if headline_token in clean(body)[:255]:
                bin_count_early += 1
        return [bin_count, bin_count_early]

    def binary_co_occurence_stops(headline, body):
        # Count how many times a token in the title
        # appears in the body text. Stopwords in the title
        # are ignored.
        bin_count = 0
        bin_count_early = 0
        for headline_token in remove_stopwords(clean(headline).split(" ")):
            if headline_token in clean(body):
                bin_count += 1
                bin_count_early += 1
        return [bin_count, bin_count_early]

    def count_grams(headline, body):
        # Count how many times an n-gram of the title
        # appears in the entire body, and intro paragraph

        clean_body = clean(body)
        clean_headline = clean(headline)
        features = []
        features = append_chargrams(features, clean_headline, clean_body, 2)
        features = append_chargrams(features, clean_headline, clean_body, 8)
        features = append_chargrams(features, clean_headline, clean_body, 4)
        features = append_chargrams(features, clean_headline, clean_body, 16)
        features = append_ngrams(features, clean_headline, clean_body, 2)
        features = append_ngrams(features, clean_headline, clean_body, 3)
        features = append_ngrams(features, clean_headline, clean_body, 4)
        features = append_ngrams(features, clean_headline, clean_body, 5)
        features = append_ngrams(features, clean_headline, clean_body, 6)
        return features

    X = []
    for i, (headline, body) in (enumerate(zip(headlines, bodies))):
        X.append(binary_co_occurence(headline, body)
                 + binary_co_occurence_stops(headline, body)
                 + count_grams(headline, body))
    return X

if __name__ == '__main__':
   pass
   #print(LIWC_lexicons('2015'))
