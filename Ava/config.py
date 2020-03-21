import os

DEBUG = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

LANGUAGE = "fr"
LANGUAGES_INFORMATION = {
    "fr": {
        "recognition": "fr-FR",
        "voice": "fr-FR",
        "steamer": "french",
        "dictionary": os.path.join(PROJECT_PATH, "..", "data", "liste_francais-utf8.txt"),
    }
}

LANGUAGES_INFORMATION_CURRENT = LANGUAGES_INFORMATION[LANGUAGE]

GOOGLE_RECOGNITION_KEY = None

