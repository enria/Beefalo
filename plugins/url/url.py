import webbrowser
import re

from plugin_api import PluginInfo, ContextApi, AbstractPlugin, get_logger
from result_model import ResultItem, ResultAction

log = get_logger("URL")


def openBrowser(url):
    webbrowser.open(url)


class URLPlugin(AbstractPlugin):
    meta_info = PluginInfo("URL", "在浏览器打开URL", "images/url_icon.png", [], False)

    def __init__(self, api: ContextApi):
        self.pattern = "^https?://.*"
        self.api = api

    def query(self, keyword, text, token=None, parent=None):
        if re.match(self.pattern, text):
            item = ResultItem(self.meta_info, "在浏览器打开URL", text, "images/url_icon.png",
                              ResultAction(openBrowser, True, text))
            return [item]
        return []
