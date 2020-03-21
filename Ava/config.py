import os

DEBUG = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

LANGUAGE = "fr"
LANGUAGES_INFORMATION = {
    "fr": {
        "recognition": "fr-FR",
        "voice": "fr-FR",
        "steamer": "french",
        "nltk": "french",
        #"dictionary": os.path.join(PROJECT_PATH, "..", "data", "liste_francais-utf8.txt"),
        "dictionary": os.path.join(PROJECT_PATH, "..", "data", "Le Mystère des XV-francais-utf-8.txt"),
        "spacy": "fr_core_news_md",
    }
}

LANGUAGES_INFORMATION_CURRENT = LANGUAGES_INFORMATION[LANGUAGE]

GOOGLE_RECOGNITION_KEY = None

