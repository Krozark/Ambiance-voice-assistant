import os

DEBUG = True
DEBUG_AUDIO_AS_TEXT = False

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_PATH, "..", "data")

LANGUAGE = "fr"
LANGUAGES_INFORMATION = {
    "fr": {
        "recognition": "fr-FR",
        "voice": "fr-FR",
        "nltk": "french",
        "input-file": os.path.join(DATA_PATH, "text-francais-utf8.txt"),
        "spacy": "fr_core_news_md",
        "data-file": os.path.join(DATA_PATH, "data.json"),
    }
}
LANGUAGES_INFORMATION_CURRENT = LANGUAGES_INFORMATION[LANGUAGE]

GOOGLE_RECOGNITION_KEY = None
