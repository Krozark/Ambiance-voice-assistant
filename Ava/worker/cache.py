import logging
from typing import Union

from Ava.core import (
    ActionList,
    IOThread,
    Cache,
)
from Ava.core.cache import CacheCouldMatchMoreError
from Ava.core.io import EmptyException

logger = logging.getLogger(__package__)


class CacheWorker(IOThread, Cache):
    def __init__(self, max_tokens=10):
        IOThread.__init__(self)
        Cache.__init__(self)
        self._tokens = []
        self.__max_tokens = max_tokens

    def _process_input_data(self, token) -> Union[ActionList, None]:
        logger.debug("CacheWorker receive token %s", token)
        self._tokens.append(token)
        m = max(self.get_depth(), self.__max_tokens)
        while len(self._tokens) > m:
            self._tokens.pop(0)

        logger.debug("CacheWorker tokens %s", self._tokens)

        index, action, it  = 0, None, 0
        for i in range(0, len(self._tokens)):
            retry = True
            while retry:
                try:
                    new_index, new_action = self.get(self._tokens[i:])
                    retry = False
                except CacheCouldMatchMoreError as e:
                    # try to add a new item
                    new_index, new_action = e.data
                    try:
                        logger.debug("try to get to get a new token")
                        data = self.input_pop(timeout=1)
                        if data is StopIteration:
                            raise StopIteration()
                        if data is not None:
                            self._tokens.append(data)
                    except EmptyException:
                        logger.warning("Impossible to get a new item")
                        retry = False
            if new_index > index and new_action:
                index, action, it = new_index, new_action, i

        if index and action:
            self._tokens = self._tokens[it + index:]
            logger.debug("CacheWorker find action '%s' at index '%s' it= %s", action, index, it)
            return action
        return None
