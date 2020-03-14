from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize


stemmer = SnowballStemmer("french")

def steam_sentence(sentence):
    words = word_tokenize(sentence)
    for w in words:
        yield stemmer.stem(w)
