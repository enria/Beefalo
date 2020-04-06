import webbrowser
import requests
import re
import json

from PyQt5.QtCore import QThread, pyqtSignal

from plugin_api import PluginInfo, ContextApi, SettingInterface, AbstractPlugin
from result_model import ResultItem, ResultAction


class SearchEngine:
    def __init__(self, name, icon, url, home):
        self.icon = icon
        self.url = url
        self.name = name
        self.home = home


class SearchSuggestion:
    def __init__(self):
        self.url = "http://suggestion.baidu.com/su"

    def suggest(self, text):
        try:
            resp = requests.get(self.url, {"wd": text})
            if resp.status_code == 200:
                sug_match = re.match(r".*(\[.*\]).*", resp.text)
                if sug_match:
                    return json.loads(sug_match.groups()[0])
        except BaseException as e:
            print(e)
        return []


class WebSearchResultItem(ResultItem):
    def __init__(self, plugin_info, engine: SearchEngine, text):
        super().__init__(plugin_info)
        if len(text.strip()):
            self.url = engine.url.format(text=text)
            self.title = text
            self.subTitle = "搜索 " + engine.name
        else:
            self.url = engine.home
            self.title = engine.name
            self.subTitle = engine.home

        self.icon = engine.icon
        self.action = ResultAction(self.openBrowser, True)

    def openBrowser(self):
        webbrowser.open(self.url)


class AsyncSuggestThread(QThread):
    sinOut = pyqtSignal([str, list])

    def __init__(self, plugin_info, parent, suggestion: SearchSuggestion, engine: SearchEngine, text, token):
        super(AsyncSuggestThread, self).__init__(parent)
        self.plugin_info = plugin_info
        self.parent = parent
        self.suggestion = suggestion
        self.text = text
        self.engine = engine
        self.token = token

    def run(self):
        texts = self.suggestion.suggest(self.text)
        results = []
        for t in texts:
            results.append(WebSearchResultItem(self.plugin_info, self.engine, t))
        self.sinOut.emit(self.token, results)


class WebSearchPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("搜索引擎", "使用默认浏览器搜索关键词", "images/web_search_icon.png",
                           [], True)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.suggestion = SearchSuggestion()
        self.engines = self.get_setting("engines")
        keys = []
        for key in self.engines:
            info = self.engines[key]
            self.engines[key] = SearchEngine(info["name"], info["icon"], info["query"], info["home"])
            keys.append(key)
        self.meta_info.keywords = keys

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if self.engines.get(keyword):
            results.append(WebSearchResultItem(self.meta_info, self.engines[keyword], text))
            if token:
                return results, AsyncSuggestThread(self.meta_info, parent, self.suggestion, self.engines[keyword], text,
                                                   token)

        return results
