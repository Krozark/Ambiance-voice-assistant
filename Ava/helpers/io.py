import logging
from queue import Queue as _Queue

logger = logging.getLogger(__package__)


class Queue(_Queue):
    def put(self, value, *args, **kwargs):
        super().put(value, *args, **kwargs)


class DuplicateOutputQueue(object):
    def __init__(self):
        self._outputs = []

    def create_output(self):
        logger.debug("Create new queue output")
        self._outputs.append(Queue())
        return self._outputs[-1]

    def put(self, value, *args, **kwargs):
        for q in self._outputs:
            q.put(value, *args, **kwargs)


class StreamMixin(object):
    def __rshift__(self, other):
        """self >> other"""
        if isinstance(other, (tuple, list)):
            output = DuplicateOutputQueue()
            self.set_output(output)
            for u in other:
                self >> u
        else:
            # self.output = other.input other.set_input(self)
            output = self.get_output()
            if isinstance(output, DuplicateOutputQueue):
                other.set_input(output.create_output())
            else:
                other.set_input(output)
        return self

    def __or__(self, other):
        """self | other"""
        return self >> other


class WithInput(StreamMixin):
    def __init__(self):
        self._input_queue = DuplicateOutputQueue()

    def set_input(self, input):
        self._input_queue = input

    def input_push(self, value) -> None:
        return self._input_queue.put(value)

    def input_pop(self):
        return self._input_queue.get()

    def input_task_done(self) -> None:
        self._input_queue.task_done()


class WithOutput(StreamMixin):
    def __init__(self):
        self._output_queue = DuplicateOutputQueue()

    def set_output(self, output):
        self._output_queue = output

    def get_output(self):
        return self._output_queue

    def output_push(self, value) -> None:
        self._output_queue.put(value)

    def output_pop(self):
        return self._output_queue.get()

    def output_task_done(self) -> None:
        self._output_queue.task_done()


class WithInputOutput(WithInput, WithOutput):
    def __init__(self):
        WithInput.__init__(self)
        WithOutput.__init__(self)




