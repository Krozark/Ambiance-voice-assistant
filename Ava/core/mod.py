import logging
from collections import defaultdict
from typing import List

from .action import ActionList, CallbackAction
from .cache import (
    CacheNodeData
)
from .utils import (
    get_register,
    WithAva
)

logger = logging.getLogger(__name__)


class Mod(CacheNodeData, WithAva):
    def __init__(self, ava, enter, exit):
        CacheNodeData.__init__(self)
        WithAva.__init__(self, ava)
        self._is_active = False
        self.regex_kwargs = defaultdict(list)
        self._non_active_nodes = CacheNodeData()

        if not isinstance(enter, (list, tuple)):
            enter = [enter]
        enter_action, enter_tokens, enter_regex, enter_data = get_register(ava, enter)[0]
        enter_action = ActionList([enter_action, CallbackAction(ava, self.activate, name="Activating mod")])
        self._non_active_nodes.register(enter_tokens, enter_action, token_regex=enter_regex)

        if not isinstance(exit, (list, tuple)):
            exit = [exit]
        exit_action, exit_tokens, exit_regex, exit_data = get_register(ava, exit)[0]
        exit_action = ActionList([exit_action, CallbackAction(ava, self.deactivate, name="Deactivating mod")])
        self.register(exit_tokens, exit_action, token_regex=exit_regex)

    def activate(self, action):
        if (self.ava._cache._mod_stack and self.ava._cache._mod_stack[-1] is not self) or not self.ava._cache._mod_stack:
            self.regex_kwargs = action._trigger_kwargs.copy()
            self._is_active = True
            logger.debug("Activating mod %s with kwargs=%s", self, self.regex_kwargs)
            self.ava._cache._mod_stack.append(self)

    def deactivate(self, action):
        if self.ava._cache._mod_stack[-1] is self:
            logger.debug("Deactivating mod %s", self)
            self._is_active = False
            self.ava._cache._mod_stack.pop()

    def get(self, tokens, depth=0, kwargs=None, results=None) -> List:
        if self._is_active:
            assert results is None and kwargs is None
            results = []
            super().get(tokens, depth, self.regex_kwargs.copy(), results)
            return results
        else:
            assert kwargs is not None and results is not None
            self._non_active_nodes.get(tokens, depth, kwargs, results)

    def __str__(self, depth=0):
        r = "  " * depth + "[Mod]"
        r += self._non_active_nodes.__str__(depth=depth + 1) + "\n"
        r += super().__str__(depth=depth + 1)
        return r
