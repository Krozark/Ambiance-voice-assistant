import logging

from pydub import AudioSegment
from sound_player import Sound

from Ava.core import (
    Action
)

logger = logging.getLogger(__name__)


class AudioFilePlayerAction(Action):
    def __init__(self, ava, filename, *args, playlist=None, loop=None, **kwargs):
        Action.__init__(self, ava, *args, name=filename, **kwargs)
        self._filename = filename
        self._playlist = playlist
        self._loop = loop

    def _do_trigger(self, playlist=None, loop=None, **kwargs) -> None:
        playlist = playlist or self._playlist
        loop = loop or self._loop
        if self.ava.config.get("audio_as_text"):
            logger.info("Play file %s to playlist %s", self._filename, playlist)
        else:
            audio = AudioSegment.from_file(self._filename)
            sound = Sound(audio)
            if loop != 1:
                sound.set_loop(loop)
            self.ava._player.enqueue(sound, playlist)


class AudioStopAction(Action):
    def __init__(self, ava, playlist=None, **kwargs):
        Action.__init__(self, ava, name=playlist, **kwargs)
        self._playlist = playlist

    def _do_trigger(self, playlist=None, **kwargs) -> None:
        playlist = playlist or self._playlist
        if self.ava.config.get("audio_as_text"):
            logger.info("Stop playlist %s", playlist)
        else:
            self.ava._player.stop(playlist=playlist)

