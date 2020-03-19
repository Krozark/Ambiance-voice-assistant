from threading import Thread as _Thread

from .io import (
    WithOutput,
    WithInput,
    WithInputOutput
)


class Thread(_Thread):
    def __init__(self):
        _Thread.__init__(self, daemon=True)
        self._is_running = False

    def stop(self) -> None:
        self._is_running = False

    def start(self) -> None:
        self._is_running = True
        super().start()


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
            self._is_running = False
