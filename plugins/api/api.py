import webbrowser
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup

from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface
from result_model import ResultItem, ResultAction

cache = {}


class APIConfig(object):
    def __init__(self, key, url, selector, content, icon, local):
        self.url = url
        self.selector = selector
        self.icon = icon
        self.key = key
        self.local = local
        self.content = content


def get_sections(config: APIConfig):
    if not config.local:
        resp = requests.get(config.url)
        dom = BeautifulSoup(resp.text, "html.parser")
    else:
        dom = BeautifulSoup(open(config.local, encoding="utf8"), "html.parser")
    sections = {}
    for ele in dom.select(config.selector):
        title, url = eval(config.content["title"]), eval(config.content["url"])
        sections[title] = config.url + url
    return sections


def build_result(plugin_info, config: APIConfig, text):
    results = []
    text = text.strip()
    sections = cache[config.key]
    for section in sections:
        if text and text.lower() not in section.lower():
            continue
        action = ResultAction(webbrowser.open, True, sections[section])
        results.append(ResultItem(plugin_info, section, sections[section], config.icon, action))
    return results


class AsyncSuggestThread(QThread):
    sinOut = pyqtSignal([str, list])

    def __init__(self, plugin_info, parent, config: APIConfig, text, token):
        super(AsyncSuggestThread, self).__init__(parent)
        self.plugin_info = plugin_info
        self.parent = parent
        self.text = text
        self.token = token
        self.config = config

    def run(self):
        cache[self.config.key] = get_sections(self.config)
        self.sinOut.emit(self.token, build_result(self.plugin_info, self.config, self.text))


class APIPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("API", "API在线文档", "images/API_icon.png",
                           [], True)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        documents = self.get_setting("documents")
        self.configs = {}
        keys = []
        for key in documents:
            document = documents[key]
            self.configs[key] = APIConfig(key, document["url"], document["section_selector"], document["content"],
                                          document["icon"],
                                          document["local"])
            keys.append(key)
        self.meta_info.keywords = keys

    def query(self, keyword, text, token=None, parent=None):
        if keyword in cache:
            return build_result(self.meta_info, self.configs[keyword], text), None
        else:
            return [], AsyncSuggestThread(self.meta_info, parent, self.configs[keyword], text, token)
