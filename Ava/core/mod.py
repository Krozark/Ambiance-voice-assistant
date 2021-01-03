import logging
from collections import defaultdict
from typing import List

from .action import ActionList, CallbackAction
from .cache import (
    CacheNodeData
)
from .utils import (
    get_register
)
from Ava.settings import settings

logger = logging.getLogger(__name__)


class Mod(CacheNodeData):
    def __init__(self, enter, exit):
        CacheNodeData.__init__(self)
        self._is_active = False
        self.regex_kwargs = defaultdict(list)
        self._non_active_nodes = CacheNodeData()

        if not isinstance(enter, (list, tuple)):
            enter = [enter]
        enter_registration = get_register(enter)
        enter_action, enter_tokens, enter_regex, enter_data = enter_registration[0]
        enter_action = ActionList([enter_action, CallbackAction(self.activate, name="Activating mod")])
        for tokens in enter_tokens:
            self._non_active_nodes.register(tokens, enter_action, token_regex=enter_regex)

        if not isinstance(exit, (list, tuple)):
            exit = [exit]
        exit_action, exit_tokens, exit_regex, exit_data = get_register(exit)[0]
        exit_action = ActionList([exit_action, CallbackAction(self.deactivate, name="Deactivating mod")])
        for tokens in exit_tokens:
            self.register(tokens, exit_action, token_regex=exit_regex)

    def activate(self, action):
        if (settings.ava._cache._mod_stack and settings.ava._cache._mod_stack[-1] is not self) or not settings.ava._cache._mod_stack:
            self.regex_kwargs = action._trigger_kwargs.copy()
            self._is_active = True
            logger.debug("Activating mod with kwargs=%s", self.regex_kwargs)
            settings.ava._cache._mod_stack.append(self)

    def deactivate(self, action):
        if settings.ava._cache._mod_stack[-1] is self:
            logger.debug("Deactivating mod")
            self._is_active = False
            settings.ava._cache._mod_stack.pop()

    def get(self, tokens, depth=0, kwargs=None, results=None) -> List:
        if self._is_active:
            if results is None:
                results = []
            if kwargs is None:
                kwargs = self.regex_kwargs.copy()
            super().get(tokens, depth, kwargs, results)
            return results
        else:
            assert kwargs is not None and results is not None
            self._non_active_nodes.get(tokens, depth, kwargs, results)

    def __str__(self, depth=0):
        r = "  " * depth + "[Mod]"
        r += self._non_active_nodes.__str__(depth=depth + 1) + "\n"
        r += super().__str__(depth=depth + 1)
        return r
