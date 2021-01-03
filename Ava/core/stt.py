import logging
from vosk import (
    Model,
    KaldiRecognizer,
    SetLogLevel
)
import os
import json
from Ava.settings import (
    settings,
    MODELS_PATH,
    AUDIO_RATE
)
from text_to_num import alpha2digit

logger = logging.getLogger(__name__)

SetLogLevel(0)


class STTMixin(object):

    _model = None
    _rec = None

    def listen(self, source, partial=False):
        self._ensure_engine()
        res = None
        if self._rec.AcceptWaveform(source):
            data = self._rec.Result()
            j = json.loads(data)
            res = j["text"]
            # res = alpha2digit(res, settings.language_data["vosk"])
        elif partial:
            data = self._rec.PartialResult()
            j = json.loads(data)
            res = j["partial"]
        return res

    def _ensure_engine(self, source=None):
        if self._model is None:
            model_path = os.path.join(MODELS_PATH, settings.language_data["vosk"])
            if not os.path.exists(model_path):
                logger.critical("Please download the model from https://alphacephei.com/vosk/models and unpack it as %s.", model_path)
                exit(1)
            self._model = Model(model_path)
            self._rec = KaldiRecognizer(self._model, AUDIO_RATE)
