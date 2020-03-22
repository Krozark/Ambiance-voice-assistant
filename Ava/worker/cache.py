import logging
from typing import List, Tuple, Union

from Ava.action import (
    ActionList
)
from Ava.utils import (
    IOThread
)

logger = logging.getLogger(__package__)


class _CacheNodeData(object):
    def __init__(self):
        self._leaf = ActionList()
        self._nodes = dict()

    def get(self, tokens: List[str], depth) -> Union[Tuple[int, ActionList], Tuple[int, None]]:
        if not tokens:
            if self._leaf:
                return depth, self._leaf
        else:
            try:
                return self._nodes[tokens[0]].get(tokens[1:], depth + 1)
            except KeyError:
                if self._leaf:
                    return depth, self._leaf

        return 0, None

    def register(self, tokens, action):
        if tokens:
            self._nodes.setdefault(tokens[0], _CacheNodeData())
            node = self._nodes.get(tokens[0])
            node.register(tokens[1:], action)
        else:
            self._leaf.append(action)

    def __str__(self, depth=0):
        r = ""
        if self._leaf:
            for x in self._leaf.__str__().split("\n"):
                r += "  " * depth + "[Action] %s \n" % x

        for key, value in self._nodes.items():
            r += "  " * depth + "[Node] %s \n" % key
            r += value.__str__(depth + 1)
        return r


class Cache(object):
    def __init__(self):
        self._root = _CacheNodeData()
        self.__max_depth = 0

    def register(self, tokens, action) -> None:
        logger.debug("Register '%s' to action '%s'", tokens, action)
        self.__max_depth = max(self.__max_depth, len(tokens))
        self._root.register(tokens, action)

    def get(self, tokens) -> Union[Tuple[int, ActionList], Tuple[int, None]]:
        return self._root.get(tokens, 0)

    def get_depth(self):
        return self.__max_depth

    def __str__(self):
        return self._root.__str__()


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



if __name__ == "__main__":
    from Ava.action import CallbackAction, AudioFilePlayerAction
    from Ava import config
    import os

    logging.basicConfig(level=logging.DEBUG)

    cache = Cache()
    tokens = "Le Mystère des XV est un roman français de Jean de La Hire publié en feuilleton en 1911 dans le quotidien Le Matin.".split()

    slice = "est un roman français".split()
    action = CallbackAction(lambda: logger.info("Action: est un roman français"), name="est un roman français")
    cache.register(slice, action)

    slice = "est un roman".split()
    action = AudioFilePlayerAction(os.path.join(config.DATA_PATH, "Splash-Ploor.mp3"), name="est un roman")
    cache.register(slice, action)

    logger.debug("Cache:\n %s", cache)

    while len(tokens):
        logger.debug("Search action for '%s'", " ".join(tokens))
        index, action = cache.get(tokens)
        if not index:
            tokens = tokens[1:]
        else:
            logger.debug("Action '%s' found with index %s", action, index)
            action.trigger()
            tokens = tokens[index:]

    logger.debug("Search action for 'est un roman anglais'")
    index, action = cache.get("est un roman anglais".split())
    action.trigger()