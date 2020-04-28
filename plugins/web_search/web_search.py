import webbrowser
import requests
import re
import json
from bs4 import BeautifulSoup

from lxml import etree
from PyQt5.QtCore import QThread, pyqtSignal

from plugin_api import PluginInfo, ContextApi, SettingInterface, AbstractPlugin, get_logger
from result_model import ResultItem, ResultAction

log = get_logger("搜索引擎")


class SearchEngine:
    def __init__(self, name, icon, url, home, suggestion):
        self.icon = icon
        self.url = url
        self.name = name
        self.home = home
        self.suggestion = suggestion
        self.direct = True


class SearchItem(object):
    def __init__(self, text, query=None, sub_title=None):
        self.text = text.strip()
        self.query = query if query else self.text
        self.sub_title = sub_title


class SearchSuggestion:
    url = ""

    def __init__(self):
        pass

    def suggest(self, text) -> list:
        pass


class BaiduSuggestion(SearchSuggestion):
    url = "http://suggestion.baidu.com/su"

    def suggest(self, text):
        try:
            resp = requests.get(self.url, {"wd": text})
            if resp.status_code == 200:
                sug_match = re.match(r".*(\[.*\]).*", resp.text)
                if sug_match:
                    return [SearchItem(text) for text in json.loads(sug_match.groups()[0])]
        except BaseException as e:
            log.error(str(e))
        return []


class GoogleSuggestion(SearchSuggestion):
    url = "http://suggestqueries.google.com/complete/search?output=toolbar&hl=en"

    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy

    def suggest(self, text):
        try:
            resp = requests.get(self.url, {"q": text}, proxies=self.proxy)
            if resp.status_code == 200:
                dom = etree.fromstring(resp.text.encode("utf-8"))
                return [SearchItem(text) for text in dom.xpath('//suggestion//@data')]
        except BaseException as e:
            log.error(str(e))
        return []


class BilibiliSuggestion(SearchSuggestion):
    url = "https://s.search.bilibili.com/main/suggest?suggest_type=accurate"

    def suggest(self, text):
        try:
            resp = requests.get(self.url, {"term": text})
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                return [SearchItem(json_data[item]["value"]) for item in json_data]
        except BaseException as e:
            log.error(e)
        return []


class ZhihuSuggestion(SearchSuggestion):
    url = "https://www.zhihu.com/api/v4/search/suggest"

    def __init__(self):
        super().__init__()

    def suggest(self, text):
        try:
            resp = requests.get(self.url, {"q": text}, headers={"User-Agent": "PostmanRuntime/7.24.0"})
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                return [SearchItem(text["query"]) for text in json_data["suggest"]]
        except BaseException as e:
            log.error(e)
        return []


class WikiSuggestion(SearchSuggestion):
    url = "https://en.wikipedia.org/w/api.php?action=opensearch&format=json"

    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy

    def suggest(self, text):
        if not text.strip():
            return []
        try:
            resp = requests.get(self.url, {"search": text}, headers={"User-Agent": "PostmanRuntime/7.24.0"},
                                proxies=self.proxy)
            if resp.status_code == 200:
                json_data = json.loads(resp.text)
                return [SearchItem(text) for text in json_data[1]]
        except BaseException as e:
            print(e)
        return []


class WebSearchResultItem(ResultItem):
    def __init__(self, plugin_info, engine: SearchEngine, item: SearchItem):
        super().__init__(plugin_info)
        if item.text:
            self.url = engine.url.format(text=item.query)
            self.title = item.text
            self.subTitle = item.sub_title if item.sub_title else "搜索 " + engine.name
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
        items = self.suggestion.suggest(self.text)
        results = []
        for item in items:
            results.append(WebSearchResultItem(self.plugin_info, self.engine, item))
        self.sinOut.emit(self.token, results)


class WebSearchPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("搜索引擎", "使用默认浏览器搜索关键词", "images/web_search_icon.png", [], True)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.engines, self.default_engine = {}, ""
        self.suggestions, self.default_suggest = {}, ""
        self.load_engines()

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if keyword and keyword != "*":
            engine = self.engines[keyword]
        else:
            engine = self.engines[self.default_engine]
        if engine.direct:
            results.append(WebSearchResultItem(self.meta_info, engine, SearchItem(text)))
        if engine.suggestion:
            suggest = self.suggestions.get(engine.suggestion)
        else:
            suggest = self.suggestions.get(self.default_suggest)
        if suggest:
            return results, AsyncSuggestThread(self.meta_info, parent, suggest, engine, text, token)
        else:
            return results, None

    def load_engines(self):
        engines = self.get_setting("engines")
        keys = ["*"]
        self.engines = {}
        for key in engines:
            info = engines[key]
            engine = SearchEngine(info["name"], info["icon"], info["query"], info["home"],
                                  info.get("suggestion"))
            if "direct" in info:
                engine.direct = info["direct"]
            self.engines[key] = engine
            keys.append(key)
        self.meta_info.keywords = keys
        self.default_engine = self.get_setting("default")["engine"]

        self.suggestions = {"Google": GoogleSuggestion(self.get_setting("proxy")),
                            "Baidu": BaiduSuggestion(),
                            "Bilibili": BilibiliSuggestion(),
                            "知乎": ZhihuSuggestion(),
                            "Wikipedia": WikiSuggestion(self.get_setting("proxy"))}
        self.default_suggest = self.get_setting("default")["suggestion"]

    def reload(self):
        SettingInterface.reload(self)
        self.load_engines()
