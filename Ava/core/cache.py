import logging
import re
from typing import List, Tuple, Union, Dict
from collections import defaultdict

from .action import ActionList, Action

logger = logging.getLogger(__package__)


class CacheResult(object):
    def __init__(self, index, action, could_more=False, kwargs=None):
        self.index = index
        self.action = action
        self.could_more = could_more
        self.kwargs = kwargs

    def __bool__(self):
        return bool(self.index or self.action)

    def __gt__(self, other):
        if not other:
            return True
        return bool(other.index > self.index and other.action)

    def __str__(self):
        return "%s" % self.__dict__

class _RegexNodeStruct(object):
    END_OF_SENTENCE_TOKEN = [".", "!", "?", "..."]

    def __init__(self, name, regex_data, node):
        self.name = name
        self.node = node
        if isinstance(regex_data, str):
            self.regex_str = regex_data
            self.regex_multiple = False
        else:
            self.regex_str = regex_data["regex"]
            self.regex_multiple = regex_data.get("multiple", False)
        self._regex_compiled = re.compile(self.regex_str)

    def match(self, token):
        return re.match(self._regex_compiled, token)

    def __str__(self, depth=0):
        return "%s(%s)" % (self.name, self.regex_str)

    def get(self, tokens: List[str], depth, regex_kwargs=None) -> Union[Tuple[int, object], Tuple[int, None]]:
        pass


class _CacheNodeData(object):
    def __init__(self):
        self._leaf = ActionList()
        self._nodes = dict()
        self._node_regex = list()  # (_RegexNodeStruct),

    # def get(self, tokens: List[str], depth, regex_kwargs=None) -> CacheResult:
    #     regex_kwargs = regex_kwargs or defaultdict(list)
    #     result = CacheResult(0, None)
    #
    #     token_len = len(tokens)
    #     if token_len > 0:
    #         token = tokens[0]
    #         try:
    #             result = self._nodes[token].get(tokens[1:], depth + 1, regex_kwargs)
    #         except KeyError:
    #             pass
    #
    #         for regex_struct in self._node_regex:
    #             if regex_struct.match(token):
    #                 regex_kwargs[regex_struct.name].append(token)
    #                 if not regex_struct.regex_multiple:  # if valid only once
    #                     return regex_struct.node.get(tokens[1:], depth + 1, regex_kwargs)
    #                 # we have to make another try
    #                 if len(tokens) == 1:  # end of tokens ?
    #                     self._leaf.set_trigger_kwargs(regex_kwargs)
    #                     data = depth, self._leaf
    #                     raise CacheCouldMatchMoreError(data)
    #
    #                 if not any(map(lambda x: tokens[1] == x, regex_struct.END_OF_SENTENCE_TOKEN)):  # end of sentence ?
    #                     return self.get(tokens[1:], depth + 1, regex_kwargs)
    #
    #     if not result and self._leaf:
    #         self._leaf.set_trigger_kwargs(regex_kwargs)
    #         result = CacheResult(depth, self._leaf)
    #     return result

    def get(self, tokens: List[str], depth, regex_kwargs) -> CacheResult:
        result = CacheResult(0, None)
        if tokens:
            token = tokens[0]
            logger.error("***************** [%s] %s", depth, token)
            try:
                result = self._nodes[token].get(tokens[1:], depth + 1, regex_kwargs.copy())
            except KeyError:
                for regex_struct in self._node_regex:
                    logger.error("******************* [%s] %s", depth, regex_struct)
                    if regex_struct.match(token):
                        regex_kwargs[regex_struct.name].append(token)
                        result = regex_struct.node.get(tokens[1:], depth + 1, regex_kwargs.copy())

        if not result and self._leaf:
            result =  CacheResult(depth, self._leaf, regex_kwargs)
        logger.error("************ Result %s", result)
        return result

    def register(self, tokens: List[str], action: Union[Action, ActionList], token_regex: Dict[str, str]) -> None:
        if not tokens:
            self._leaf.append(action)
        else:
            token = tokens[0]
            if token not in token_regex:
                self._nodes.setdefault(token, _CacheNodeData())
                node = self._nodes.get(token)
            else:
                for regex_struct in self._node_regex:
                    if regex_struct.name == token:
                        node = regex_struct.node
                        break
                else:
                    self._node_regex.append(_RegexNodeStruct(token, token_regex[token], _CacheNodeData()))
                    node = self._node_regex[-1].node
            node.register(tokens[1:], action, token_regex)

    def __str__(self, depth=0):
        r = ""
        if self._leaf:
            for x in self._leaf.__str__().split("\n"):
                r += "  " * depth + "[Action] %s \n" % x

        for key, value in self._nodes.items():
            r += "  " * depth + "[Node] %s \n" % key
            r += value.__str__(depth + 1)

        for regex_struct in self._node_regex:
            r += "  " * depth + "[Node Regex] %s \n" % regex_struct
            r += regex_struct.node.__str__(depth + 1)
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

    def get(self, tokens) -> CacheResult:
        return self._root.get(tokens, 0,  defaultdict(list))

    def get_depth(self):
        return self.__max_depth

    def __str__(self):
        return self._root.__str__()
