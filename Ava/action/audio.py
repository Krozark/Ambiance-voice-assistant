import logging

from pydub import AudioSegment
from pydub.playback import play

from Ava import config
from Ava.core import (
    Action
)

logger = logging.getLogger(__name__)


class AudioFilePlayerAction(Action):
    def __init__(self, filename, *args, **kwargs):
        self._filename = filename
        super().__init__(*args, name=filename, **kwargs)

    def _do_trigger(self, **kwargs) -> None:
        if config.DEBUG_AUDIO_AS_TEXT:
            logger.info("Play file %s", self._filename)
        else:
            audio = AudioSegment.from_file(self._filename)
            play(audio)


