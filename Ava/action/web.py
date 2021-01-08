import logging
import webbrowser

import wikipedia

from Ava.core import (
    Action,
    TTSMixin
)
from Ava.settings import settings

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
        search = search or self._search or ""
        base_url = base_url or self._base_url
        webbrowser.open_new_tab(base_url + search)


class WikipediaSearchAction(Action):
    def __init__(self, *args, search=None, **kwargs):
        super().__init__(*args, name=search, **kwargs)
        self._search = search

    def _do_trigger(self, *args, search=None, **kwargs) -> None:
        search = search or self._search or ""
        wikipedia.set_lang(settings.language_data["wikipedia"])
        key = wikipedia.search(search, results=1)
        if key:
            webbrowser.open_new_tab(wikipedia.page(key[0]).url)


class WikipediaSearchTTSAction(Action, TTSMixin):
    def __init__(self, *args, search=None, sentences=2, **kwargs):
        Action.__init__(self, *args, name=search, **kwargs)
        TTSMixin.__init__(self)
        self._search = search
        self._sentences = sentences

    def _do_trigger(self, *args, search=None, sentences=None, **kwargs) -> None:
        search = search or self._search or ""
        sentences = sentences or self._sentences or 2
        wikipedia.set_lang(settings.language_data["wikipedia"])
        key = wikipedia.search(search, results=1)
        if key:
            self.say(wikipedia.summary(key[0], sentences=sentences))
