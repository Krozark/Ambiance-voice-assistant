import logging
import webbrowser

from Ava.core import (
    Action
)

logger = logging.getLogger(__name__)


class WebBrowserAction(Action):
    def __init__(self, *args, url=None, **kwargs):
        super().__init__(*args, name=url, **kwargs)
        self._url = url

    def _do_trigger(self, *args, url=None, **kwargs) -> None:
        url = url or self._url or ""
        webbrowser.open_new_tab(url)


class WebBrowserSearchAction(Action):
    def __init__(self, *args, search=None, base_url=None, **kwargs):
        super().__init__(*args, name=search, **kwargs)
        self._search = search
        self._base_url = base_url or "https://duckduckgo.com/?q="

    def _do_trigger(self, *args, search=None, base_url=None, **kwargs) -> None:
        search =  search or self._search or ""
        base_url = base_url or self._base_url
        webbrowser.open_new_tab(self._base_url + search)