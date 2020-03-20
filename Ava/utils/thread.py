from threading import Thread as _Thread
import logging
from .io import (
    WithOutput,
    WithInput,
    WithInputOutput
)


logger = logging.getLogger(__package__)


class Thread(_Thread):
    def __init__(self):
        _Thread.__init__(self, daemon=True)
        self._is_running = False

    def stop(self) -> None:
        logger.debug("Stop thread {}".format(type(self).__name__))
        self._is_running = False

    def start(self) -> None:
        logger.debug("Start thread {}".format(type(self).__name__))
        self._is_running = True
        super().start()

    def _bootstrap(self):
        super()._bootstrap()
        logger.debug("Thread stopped {}".format(type(self).__name__))


class OThread(Thread, WithOutput):
    def __init__(self):
        Thread.__init__(self)
        WithOutput.__init__(self)


class IThread(Thread, WithInput):
    def __init__(self):
        Thread.__init__(self)
        WithInput.__init__(self)

    def stop(self) -> None:
        super().stop()
        self.input_push(None)

    def _process_input_data(self, data) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        # this runs in a background thread
        try:
            while self._is_running:
                data = self.input_pop()
                if data is None:
                    raise StopIteration
                self._process_input_data(data)
                self.input_task_done()
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False


class IOThread(Thread, WithInputOutput):
    def __init__(self):
        Thread.__init__(self)
        WithInputOutput.__init__(self)

    def stop(self) -> None:
        super().stop()
        self.input_push(None)

    def _process_input_data(self, data):
        raise NotImplementedError()

    def run(self) -> None:
        # this runs in a background thread
        try:
            while self._is_running:
                data = self.input_pop()
                if data is None:
                    raise StopIteration
                out = self._process_input_data(data)
                self.input_task_done()
                self.output_push(out)
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False
