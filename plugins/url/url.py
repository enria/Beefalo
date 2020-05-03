import webbrowser
import re
import requests
from urllib import parse

from PyQt5.QtGui import QGuiApplication

from plugin_api import PluginInfo, ContextApi, AbstractPlugin, get_logger
from result_model import ResultItem, ResultAction, MenuItem

log = get_logger("URL")


def openBrowser(url):
    webbrowser.open(url)


def shorten_url(url):
    resp = requests.get("http://mrw.so/api.htm",
                        {"url": url, "key": "5e987fc544bb353dc4015768@ad921" +
                                            "abbcf47edc3cff0d2b7aaf1847c"})
    return resp.text


class URLPlugin(AbstractPlugin):
    meta_info = PluginInfo("URL", "在浏览器打开URL", "images/url_icon1.png", ["surl", "*"], False)

    def __init__(self, api: ContextApi):
        self.pattern = "^https?://.+"
        self.api = api

    def generate(self, text):
        short_url = shorten_url(text)
        item = ResultItem(self.meta_info, short_url, "点击复制", "images/url_copy.png",
                          ResultAction(QGuiApplication.clipboard().setText, True, short_url))
        item.menus = [MenuItem(" 在浏览器中打开", ResultAction(openBrowser, True, short_url))]
        self.api.change_results([item])

    def query(self, keyword, text, token=None, parent=None):
        text = text.strip()
        if keyword == "surl" and text:
            item = ResultItem(self.meta_info, "使用 mrw.so 生成短链", text, "images/url_icon1.png",
                              ResultAction(self.generate, False, text))
            return [item]
        elif re.match(self.pattern, text):
            item = ResultItem(self.meta_info, "在浏览器打开URL", text, "images/url_icon1.png",
                              ResultAction(openBrowser, True, text))
            return [item]
        return []
