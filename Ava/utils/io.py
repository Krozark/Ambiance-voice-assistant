import logging
from queue import Queue

logger = logging.getLogger(__package__)


class DuplicateOutputQueue(object):
    """
    Class tha internally manage a pool of Queue(). Each time an item is put()
    this item is put into all the queues. This is usefull to manage a single entry with multiple outputs.
    """
    def __init__(self):
        self._outputs = []

    def create_output(self) -> Queue:
        """
        Creat a new output
        :return: the new output to use (Queue)
        """
        logger.debug("Create new queue as output")
        self._outputs.append(Queue())
        return self._outputs[-1]

    def add_output(self, queue: Queue) -> None:
        """
        Add an existing output to the internal list
        :param queue: Queue to add
        """
        logger.debug("add existing queue as output")
        self._outputs.append(queue)

    def put(self, value, *args, **kwargs) -> None:
        """
        Put duplicate an item to all outputs
        :param value: item to send
        """
        for q in self._outputs:
            q.put(value, *args, **kwargs)


class StreamMixin(object):
    """
    Allow the class to us ">>" to define it's output(s)
    self >> other
    """
    def __rshift__(self, other):
        if isinstance(other, (tuple, list)):
            old = self.get_output()
            if not isinstance(old, DuplicateOutputQueue):
                new = DuplicateOutputQueue()
                new.add_output(old)
                self.set_output(new)
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


class WithInput(StreamMixin):
    """
    Class that contain a internal Queue as input
    """
    def __init__(self):
        self._input_queue = None

    def set_input(self, input):
        self._input_queue = input

    def input_push(self, value) -> None:
        return self._input_queue.put(value)

    def input_pop(self):
        return self._input_queue.get()

    def input_task_done(self) -> None:
        self._input_queue.task_done()


class WithOutput(StreamMixin):
    """
    Class that contain a internal Queue as output
    """
    def __init__(self):
        self._output_queue = Queue()

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
    """
    Class that contain a internal Queue as input, and another as output
    """
    def __init__(self):
        WithInput.__init__(self)
        WithOutput.__init__(self)




