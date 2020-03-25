import logging
import re
from typing import List, Tuple, Union, Dict

from .action import ActionList, Action

logger = logging.getLogger(__package__)


class _CacheNodeData(object):
    def __init__(self):
        self._leaf = ActionList()
        self._nodes = dict()
        self._node_regex = list()  # (varname, regex_str, regex_compiled, node),

    def get(self, tokens: List[str], depth, regex_kwargs) -> Union[Tuple[int, object], Tuple[int, None]]:
        if not tokens:
            if self._leaf:
                return depth, self._leaf
        else:
            token = tokens[0]
            try:
                return self._nodes[token].get(tokens[1:], depth + 1, regex_kwargs)
            except KeyError:
                pass

            for varname, regex_str, regex_compiled, node  in self._node_regex:
                m = re.match(regex_compiled, token)
                if m:
                    regex_kwargs[varname] = token
                    return node.get(tokens[1:], depth + 1, regex_kwargs)
            if self._leaf:
                return depth, self._leaf
        return 0, None

    def register(self, tokens: List[str], action: Union[Action, ActionList], token_regex: Dict[str, str]):
        if not tokens:
            self._leaf.append(action)
        else:
            token = tokens[0]
            if token not in token_regex:
                self._nodes.setdefault(token, _CacheNodeData())
                node = self._nodes.get(token)
            else:
                for varname, regex_str, regex_compiled, node in self._node_regex:
                    if varname == token:
                        break
                else:
                    regex_str = token_regex[token]
                    regex_compiled = re.compile(regex_str)
                    self._node_regex.append((
                        token,
                        regex_str,
                        regex_compiled,
                        _CacheNodeData()
                    ))
                    node = self._node_regex[-1][3]
            node.register(tokens[1:], action, token_regex=token_regex)

    def __str__(self, depth=0):
        r = ""
        if self._leaf:
            for x in self._leaf.__str__().split("\n"):
                r += "  " * depth + "[Action] %s \n" % x

        for key, value in self._nodes.items():
            r += "  " * depth + "[Node] %s \n" % key
            r += value.__str__(depth + 1)

        for varname, regex_str, regex_compiled, node in self._node_regex:
            r += "  " * depth + "[Node Regex] %s(%s) \n" % (varname, regex_str)
            r += node.__str__(depth + 1)
        return r


class Cache(object):
    def __init__(self):
        self._root = _CacheNodeData()
        self.__max_depth = 0

    def register(self, tokens: List[str], action: Union[Action, ActionList], token_regex: Dict[str, str]=None) -> None:
        assert isinstance(action, (Action, ActionList))
        token_regex = token_regex or dict()
        logger.debug("Register %s to action '%s', token_regex=%s", tokens, action, token_regex)

        self.__max_depth = max(self.__max_depth, len(tokens))
        self._root.register(tokens, action, token_regex)

    def get(self, tokens) -> Union[Tuple[int, object, dict], Tuple[int, None, dict]]:
        regex_kwargs = {}
        index, action = self._root.get(tokens, 0, regex_kwargs)
        return index, action, regex_kwargs

    def get_depth(self):
        return self.__max_depth

    def __str__(self):
        return self._root.__str__()
