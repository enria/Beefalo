import webbrowser
import requests
import re, json
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from ResultModel import ResultItem, ResultAction
import threading


class DictResultItem(ResultItem):
    def __init__(self, origin, translation):
        super().__init__()
        self.title = translation
        self.subTitle = origin
        self.icon = "dict_result.png"
        self.action = ResultAction(None, True)


class DictPlugin:
    keywords = {"dict"}

    def __init__(self):
        self.callback = False
        threading.Thread(target=self.loadDict).start()
        self.localDict = {}

    def loadDict(self):
        with open("resource/英汉词典TXT格式.txt", "r", encoding="UTF-16") as dicFile:
            for line in dicFile.readlines():
                match = re.match(r"(.+?)\s+(.+)", line)
                if match:
                    ori, tra = match.groups()[0], match.groups()[1]
                    if self.localDict.get(ori):
                        self.localDict[ori].append(tra)
                    else:
                        self.localDict[ori] = [tra]

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if self.localDict.get(text):
            for translation in self.localDict[text]:
                results.append(DictResultItem(text, translation))
        return results
