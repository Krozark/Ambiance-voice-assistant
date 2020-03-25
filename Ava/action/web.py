import logging
import webbrowser

from Ava.core import (
    Action
)

logger = logging.getLogger(__package__)


class WebBrowserAction(Action):
    def __init__(self, *args, url=None, **kwargs):
        super().__init__(*args, name=url, **kwargs)
        self._url = url

    def _do_trigger(self, *args, url=None, **kwargs) -> None:
        url = url or self._url or ""
        webbrowser.open_new_tab(url)