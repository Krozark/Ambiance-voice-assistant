from Ava.core import (
    IThread,
)


class ActionWorker(IThread):
    def _process_input_data(self, data) -> None:
        data.trigger()
