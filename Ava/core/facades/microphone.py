import enum


class MicrophoneState(enum.Enum):
    ready = 1
    recording = 2


# class MicrophoneStream(object):
#     pass
#

class MicrophoneFacade(object):
    def __init__(self):
        super().__init__()
        self.state = MicrophoneState.ready
        self.stream = None

    def start(self):
        self.state = MicrophoneState.recording
        self._start()
        return self.stream

    def _start(self):
        raise NotImplementedError()

    def stop(self):
        self._stop()
        self.state = MicrophoneState.ready

    def _stop(self):
        raise NotImplementedError()

