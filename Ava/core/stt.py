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
    LANG_PATH,
    MODEL_DIRNAME,
    AUDIO_RATE
)
import requests
import tempfile
from zipfile import ZipFile
import humanize

logger = logging.getLogger(__name__)

SetLogLevel(0)


class STTMixin(object):

    _model = None
    _rec = None

    def __init__(self):
        self._ensure_engine()

    def listen(self, source, partial=False):
        res = None
        if self._rec.AcceptWaveform(source):
            data = self._rec.Result()
            j = json.loads(data)
            res = j["text"]
        elif partial:
            data = self._rec.PartialResult()
            j = json.loads(data)
            res = j["partial"]
        return res

    def _ensure_engine(self, source=None):
        if self._model is None:
            model_path = os.path.join(LANG_PATH, settings.get_language(), MODEL_DIRNAME)
            if not os.path.exists(model_path):
                url = settings.language_data["vosk-model"]
                logger.warning("No model found in %s. Downloading %s", model_path, url)
                with requests.Session() as session:
                    with session.get(url, stream=True) as r:
                        r.raise_for_status()
                        # stream content
                        # with open(model_path + ".zip", "wb") as tmpf:
                        with tempfile.NamedTemporaryFile() as tmpf:
                            logger.debug("Downloading in %s", tmpf.name)
                            # write content to tempory file
                            size = int(r.headers.get("content-length", 0))
                            human_size = humanize.naturalsize(size)
                            current = 0
                            for chunk in r.iter_content(chunk_size=1024 * 1024):
                                l = len(chunk)
                                if l:
                                    current += l
                                    progess = (current / size) * 100
                                    logger.debug("Writing into %s. %s/%s : %.2f%%", tmpf.name, humanize.naturalsize(current), human_size, progess)
                                    tmpf.write(chunk)
                            tmpf.flush()
                            tmpf.seek(0)
                            logger.debug("Downloading model finished")
                            # unzip content
                            root = None
                            with ZipFile(tmpf.name, "r") as zf:
                                extract_path = os.path.join(LANG_PATH, settings.get_language())
                                root = os.path.join(extract_path, zf.namelist()[0])
                                logger.debug("Decompressing %s into %s", tmpf.name, extract_path)
                                zf.extractall(extract_path)
                        logger.debug("Renaming %s into %s", root, model_path)
                        os.rename(root, model_path)

            if not os.path.exists(model_path):
                logger.critical("Please download the model from https://alphacephei.com/vosk/models and unpack it as %s.", model_path)
                exit(1)
            logger.info("Loading Kaldi module. Please wait.")
            self._model = Model(model_path)
            self._rec = KaldiRecognizer(self._model, AUDIO_RATE)
            logger.info("Kaldi module loaded")
