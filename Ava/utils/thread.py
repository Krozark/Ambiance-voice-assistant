from threading import Thread as _Thread
import logging
from .io import (
    WithOutput,
    WithInput,
    WithInputOutput
)


logger = logging.getLogger(__package__)


class Thread(_Thread):
    """
    Add some feature to Thread class
    """
    def __init__(self):
        _Thread.__init__(self, daemon=True)
        self._is_running = False

    def stop(self) -> None:
        """Stop the current thread (non blocking)"""
        logger.debug("Stop thread {}".format(type(self).__name__))
        self._is_running = False

    def start(self) -> None:
        """Stop the thread (non blocking)"""
        logger.debug("Start thread {}".format(type(self).__name__))
        self._is_running = True
        super().start()

    def _bootstrap(self):
        super()._bootstrap()
        logger.debug("Thread stopped {}".format(type(self).__name__))


class OThread(Thread, WithOutput):
    """
    Thread class that have output.
    You need to override run().
    """
    def __init__(self):
        Thread.__init__(self)
        WithOutput.__init__(self)

    def stop(self) -> None:
        """Stop the current thread (non blocking)"""
        super().stop()
        self.output_push(None)


class IThread(Thread, WithInput):
    """
    Thread class that have input and process them one by one.
    You need to overwrite _process_input_data()
    """
    def __init__(self):
        Thread.__init__(self)
        WithInput.__init__(self)

    def stop(self) -> None:
        """Stop the current thread (non blocking)"""
        super().stop()
        self._input_push(StopIteration)

    def _process_input_data(self, data) -> None:
        """
        Process one item
        :param data:item to precess
        :return:Nothing
        """
        raise NotImplementedError()

    def run(self) -> None:
        """Thread implementation"""
        # this runs in a background thread
        try:
            while self._is_running:
                data = self.input_pop()
                if data is StopIteration:
                    raise StopIteration()
                self._process_input_data(data)
                self.input_task_done()
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False


class IOThread(Thread, WithInputOutput):
    """
    Thread class that have input and output.
     Process input one item at the time, and send the result to it's output.
    You need to overwrite _process_input_data()
    """
    def __init__(self):
        Thread.__init__(self)
        WithInputOutput.__init__(self)

    def stop(self) -> None:
        """Stop the current thread (non blocking)"""
        super().stop()
        self._input_push(StopIteration)
        self.output_push(None)

    def _process_input_data(self, data):
        """
        Process one item
        :param data:item to precess
        :return: Somthing to send to output
        """
        raise NotImplementedError()

    def run(self) -> None:
        """Thread implementation"""
        try:
            while self._is_running:
                data = self.input_pop()
                if data is StopIteration:
                    raise StopIteration()
                out = self._process_input_data(data)
                self.input_task_done()
                self.output_push(out)
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False
