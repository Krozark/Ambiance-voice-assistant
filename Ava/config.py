import os

DEBUG = True
DEBUG_AUDIO_AS_TEXT = DEBUG

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_PATH, "..", "data")

LANGUAGE = "fr"
LANGUAGES_INFORMATION = {
    "fr": {
        "recognition": "fr-FR",
        "voice": "fr-FR",
        "nltk": "french",
        #"data-file": os.path.join(PROJECT_PATH, "..", "data", "liste_francais-utf8.txt"),
        "data-file": os.path.join(DATA_PATH, "text-francais-utf8.txt"),
        "spacy": "fr_core_news_md",
    }
}

LANGUAGES_INFORMATION_CURRENT = LANGUAGES_INFORMATION[LANGUAGE]

GOOGLE_RECOGNITION_KEY = None

