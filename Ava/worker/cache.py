import logging
from typing import Union

from Ava.core import (
    ActionList,
    IOxThread,
    Cache,
    Worker
)

logger = logging.getLogger(__name__)


class CacheWorker(Worker, IOxThread, Cache):
    def __init__(self, **kwargs):
        Worker.__init__(self, **kwargs)
        IOxThread.__init__(self)
        Cache.__init__(self)
        self._tokens = []

    def _process_tokens(self):
        logger.debug("Precessing tokens %s", self._tokens)
        results = self.get(self._tokens)
        results = sorted(results)
        logger.debug("Found %s results for tokens %s => %s", len(results), self._tokens, ["<%s>" % x for x in results])
        token = None
        if not results:
            self._tokens.pop(0)
        else:
            if results[-1].if_deeper():
                logger.debug("Try to get a new token")
                token = self.input_pop(timeout=1)
                if token is None:
                    logger.debug("Impossible to get new token")
        return results, token

    def _get_action(self, result):
        action = result.action
        action.set_trigger_kwargs(result.kwargs)
        return action

    def _process_results(self, results):
        action = None
        if results:
            try:
                # get most important result
                result = results.pop()
                while result.if_deeper():
                    result = results.pop()
                self._tokens = self._tokens[result.length:]
                logger.debug("Find action '%s'", result)
                action = self._get_action(result)
            except IndexError:
                pass
        return action

    def _process_input_data(self, token) -> Union[ActionList, None]:
        logger.debug("Receive token '%s'", token)
        self._tokens.append(token)
        while self._tokens:
            while True:
                results, token = self._process_tokens()
                if token is None:
                    break
                else:
                    self._tokens.append(token)
            yield self._process_results(results)
