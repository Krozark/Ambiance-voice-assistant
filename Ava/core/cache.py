import logging
from typing import List, Tuple, Union

from .action import ActionList, Action

logger = logging.getLogger(__package__)


class _CacheNodeData(object):
    def __init__(self):
        self._leaf = ActionList()
        self._nodes = dict()

    def get(self, tokens: List[str], depth) -> Union[Tuple[int, object], Tuple[int, None]]:
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

    def register(self, tokens: List[str], action: Union[Action, ActionList]):
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

    def register(self, tokens: List[str], action: Union[Action, ActionList]) -> None:
        assert isinstance(action, (Action, ActionList))
        logger.debug("Register %s to action '%s'", tokens, action)

        self.__max_depth = max(self.__max_depth, len(tokens))
        self._root.register(tokens, action)

    def get(self, tokens) -> Union[Tuple[int, object], Tuple[int, None]]:
        return self._root.get(tokens, 0)

    def get_depth(self):
        return self.__max_depth

    def __str__(self):
        return self._root.__str__()
