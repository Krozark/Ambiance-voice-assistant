from queue import Queue


class WithInput(object):
    def __init__(self):
        self._input_queue = Queue()

    def set_input(self, input):
        pass

    def input_push(self, value) -> None:
        return self._input_queue.put(value)

    def input_pop(self):
        return self._input_queue.get()

    def input_task_done(self) -> None:
        self._input_queue.task_done()


class WithOutput(object):
    def __init__(self):
        self._output_queue = Queue()

    def set_output(self, output):
        pass

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