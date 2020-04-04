import webbrowser
import requests
import re, json

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from ResultModel import ResultItem, ResultAction


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
        result = []
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
    def __init__(self, engine: SearchEngine, text):
        super().__init__()
        if len(text.strip()):
            self.url = engine.url.format(text)
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

    def __init__(self, parent, suggestion: SearchSuggestion, engine: SearchEngine, text, token):
        super(AsyncSuggestThread, self).__init__(parent)
        self.parent = parent
        self.suggestion = suggestion
        self.text = text
        self.engine = engine
        self.token = token

    def run(self):
        texts = self.suggestion.suggest(self.text)
        results = []
        for t in texts:
            results.append(WebSearchResultItem(self.engine, t))
        self.sinOut.emit(self.token, results)


class WebSearchPlugin:
    engines = {
        "g": SearchEngine("Google", "web_search_google.png",
                          "https://www.google.com/search?q={}", "https://www.google.com"),
        "bing": SearchEngine("Bing", "web_search_bing.png", "https://www.bing.com/search?q={}",
                             "https://www.bing.com"),
        "you": SearchEngine("Youtube", "web_search_youtube.png",
                            "https://www.youtube.com/results?search_query={}",
                            "https://www.youtube.com"),
        "bili": SearchEngine("Bilibili", "web_search_bilibili.png",
                             "https://search.bilibili.com/all?keyword={}",
                             "https://www.bilibili.com/"),
        "baidu": SearchEngine("Baidu", "web_search_baidu.png",
                              "https://www.baidu.com/#ie=UTF-8&wd={}",
                              "https://www.baidu.com")
    }
    keywords = list(engines.keys())
    _name_, _desc_, _icon_ = "搜索引擎", "使用默认浏览器搜索关键词", "web_search_icon.png"

    def __init__(self, open_sug=True):
        self.callback = False
        if open_sug:
            self.suggestion = SearchSuggestion()
            self.callback = True

    def query(self, keyword, text, token=None, parent=None):
        results = []

        if self.engines.get(keyword):
            results.append(WebSearchResultItem(self.engines[keyword], text))
            if token:
                return results, AsyncSuggestThread(parent, self.suggestion, self.engines[keyword], text, token)

        return results
