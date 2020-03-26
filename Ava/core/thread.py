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

    def input_pop(self, timeout=None):
        res = self._input_queue.get(timeout=timeout)
        self.input_task_done()
        return res

    def run(self) -> None:
        """Thread implementation"""
        # this runs in a background thread
        try:
            while self._is_running:
                data = self.input_pop()
                if data is StopIteration:
                    raise StopIteration()
                if data is not None:
                    self._process_input_data(data)
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False


class _IOThreadBase(Thread, WithInputOutput):
    def __init__(self):
        Thread.__init__(self)
        WithInputOutput.__init__(self)

    def input_pop(self, timeout=None):
        res = self._input_queue.get(timeout=timeout)
        self.input_task_done()
        return res

    def stop(self) -> None:
        """Stop the current thread (non blocking)"""
        super().stop()
        self._input_push(StopIteration)
        self.output_push(None)


class IOThread(_IOThreadBase):
    """
    Thread class that have input and output.
    Process input one item at the time, and send the result to it's output.
    You need to overwrite _process_input_data()
    """
    def _process_input_data(self, data):
        """
        Process one item
        :param data:item to precess
        :return: Something to send to output
        """
        raise NotImplementedError()

    def run(self) -> None:
        """Thread implementation"""
        try:
            while self._is_running:
                data = self.input_pop()
                if data is StopIteration:
                    raise StopIteration()
                if data is not None:
                    out = self._process_input_data(data)
                    if out is not None:
                        self.output_push(out)
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False


class IOxThread(_IOThreadBase):
    """
    Thread class that have input and multiple output.
    Process input one item at the time, and send the result to it's output.
    You need to overwrite _process_input_data()
    """

    def _process_input_data(self, data) -> list:
        """
        Process one item and yield any number of outputs
        :param data:item to process
        :return: None
        """
        raise NotImplementedError()

    def run(self) -> None:
        """Thread implementation"""
        try:
            while self._is_running:
                data = self.input_pop()
                if data is StopIteration:
                    raise StopIteration()
                if data is not None:
                    for out in self._process_input_data(data):
                        if out is not None:
                            self.output_push(out)
        except StopIteration:
            logger.debug("Thread {} receive a stop iteration".format(type(self).__name__))
            self._is_running = False
