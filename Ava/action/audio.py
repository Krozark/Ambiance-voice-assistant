import logging

from pydub import AudioSegment
from sound_player import Sound

from Ava.core import (
    Action
)

logger = logging.getLogger(__name__)


class AudioFilePlayerAction(Action):
    def __init__(self, ava, filename, *args, playlist="default", **kwargs):
        Action.__init__(self, ava, *args, name=filename, **kwargs)
        self._filename = filename
        self._playlist = playlist

    def _do_trigger(self, **kwargs) -> None:
        if self.ava.config.get("audio_as_text"):
            logger.info("Play file %s to playlist %s", self._filename, self._playlist)
        else:
            audio = AudioSegment.from_file(self._filename)
            sound = Sound(audio)
            self.ava._player.enqueue(sound, self._playlist)
