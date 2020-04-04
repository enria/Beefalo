import re, json
from PyQt5.QtCore import QThread, pyqtSignal, QObject

from Plugin import AbstractPlugin
from ResultModel import ResultItem, ResultAction
import requests
import uuid
from hashlib import sha256
from datetime import datetime


class DictResultItem(ResultItem):
    icons = {"basic": "dict_basic.png", "translate": "dict_translate.png"}

    def __init__(self, title, subTitle, resultType):
        super().__init__()
        self.title = title
        self.subTitle = subTitle
        self.icon = self.icons[resultType]
        self.action = ResultAction(None, True)


class YoudaoApiThread(QThread):
    sinOut = pyqtSignal([str, list])

    def __init__(self, parent, text, token):
        super(YoudaoApiThread, self).__init__(parent)
        self.parent = parent
        self.text = text
        self.token = token

    def run(self):
        t = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
        salt = str(uuid.uuid1())
        sec = "l75XR7v6A5pFIe59EZ7fcfJtiOWx82SS"
        params = {"q": self.text, "from": "auto", "to": "auto",
                  "appKey": "2e6335573f802c90",
                  "salt": salt, "signType": "v3", "curtime": str(t)}

        shaHash = sha256()
        shaHash.update((params["appKey"] + params["q"] + params["salt"] + params["curtime"] + sec).encode(
            'utf-8'))
        params["sign"] = shaHash.hexdigest()

        try:
            results = []
            resp = requests.get("https://openapi.youdao.com/api", params)
            apiResp = json.loads(resp.text)
            if apiResp.get("basic"):
                if apiResp["basic"].get("us-phonetic"):
                    phonetic, wfs = "美[{}]  英[{}]".format(apiResp["basic"].get("us-phonetic"),
                                                          apiResp["basic"].get("uk-phonetic")), ""
                    if apiResp["basic"].get("wfs"):
                        for wf in apiResp["basic"]["wfs"]:
                            wfs += "{}：{}；".format(wf["wf"]["name"], wf["wf"]["value"])
                        results.append(DictResultItem(wfs, phonetic, "basic"))
                    else:
                        results.append(DictResultItem(phonetic, None, "basic"))

                if apiResp["basic"].get("explains"):
                    for exp in apiResp["basic"]["explains"]:
                        results.append(DictResultItem(exp, self.text, "translate"))
            self.sinOut.emit(self.token, results)
        except BaseException as e:
            print(e)


class DictPlugin(AbstractPlugin):
    keywords = ["dict"]
    _name_, _desc_, _icon_ = "在线词典", "使用有道云接口的在线典", "dict_basic.png"

    def __init__(self):
        self.callback = True
        # threading.Thread(target=self.loadDict).start()
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
        if len(text.strip()):
            results = []
            if self.localDict.get(text):
                for translation in self.localDict[text]:
                    results.append(DictResultItem(translation, text))
            return results, YoudaoApiThread(parent, text, token)
        else:
            return [], None
