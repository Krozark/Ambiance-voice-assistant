import logging
from typing import Union

from Ava.action import (
    ActionList
)
from Ava.utils import (
    IOThread,
    Cache
)

logger = logging.getLogger(__package__)


class CacheWorker(IOThread, Cache):
    def __init__(self, max_tokens=10):
        IOThread.__init__(self)
        Cache.__init__(self, ActionList)
        self._tokens = []
        self.__max_tokens = max_tokens

    def _process_input_data(self, token) -> Union[ActionList, None]:
        logger.debug("CacheWorker receive token %s", token)
        self._tokens.append(token)
        m = max(self.get_depth(), self.__max_tokens)
        while len(self._tokens) > m:
            self._tokens.pop(0)

        logger.debug("CacheWorker tokens %s", self._tokens)

        index, action, it = 0, None, 0
        for i in range(0, len(self._tokens)):
            new_index, new_action = self.get(self._tokens[i:])
            if new_index > index and new_action:
                index, action, it = new_index, new_action, i

        if index and action:
            self._tokens = self._tokens[it + index:]
            logger.debug("CacheWorker find action '%s' at index '%s' it= %s", action, index, it)
            return action
        return None
