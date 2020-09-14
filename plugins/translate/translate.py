import re, json
import os
import requests
import uuid
from hashlib import sha256
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent

from plugin_api import PluginInfo, ContextApi, AbstractPlugin, get_logger
from result_model import ResultItem, ResultAction

log = get_logger("在线词典")


class DictResultItem(ResultItem):
    icons = {"basic": "images/dict_basic.png", "translate": "images/dict_translate.png"}

    def __init__(self, plugin_info, title, subTitle, resultType):
        super().__init__(plugin_info, title, subTitle)
        self.icon = self.icons[resultType]
        self.action = ResultAction(None, True)


sound_url = ""


def play_sound(plugin_info, api, url):
    api.play_media(QMediaContent())
    global sound_url
    if url != sound_url:
        resp = requests.get(url)
        with open(os.path.join(plugin_info.path, "speech.mp3"), "wb") as sound_file:
            sound_file.write(resp.content)
        sound_url = url
    api.play_media(QMediaContent(QUrl.fromLocalFile(os.path.join(plugin_info.path, "speech.mp3"))))
    # api.play_media(QUrl(url))


class YoudaoApiThread(QThread):
    sin_out = pyqtSignal([str, list])

    def __init__(self, plugin_info, parent, api, text, token):
        super(YoudaoApiThread, self).__init__(parent)
        self.parent = parent
        self.text = text
        self.token = token
        self.plugin_info = plugin_info
        self.api = api

    def run(self):
        t = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
        salt = str(uuid.uuid1())
        sec = "l75XR7v" + "6A5pFI" + "e59EZ7f" + "cfJtiOW" + "x82SS"
        params = {"q": self.text, "from": "auto", "to": "auto",
                  "app" + "Key": "2e633" + "5573f80" + "2c90",
                  "salt": salt, "sign" + "Type": "v3", "curtime": str(t)}

        shaHash = sha256()
        shaHash.update((params["app" + "Key"] + params["q"] + params["salt"] + params["curtime"] + sec).encode(
            'utf-8'))
        params["si" + "gn"] = shaHash.hexdigest()

        try:
            results = []
            resp = requests.get("https://open" + "api.you" + "dao.com/api", params)
            apiResp = json.loads(resp.text)
            if apiResp.get("basic"):
                if apiResp["basic"].get("us-phonetic"):
                    phonetic, wfs = "美[{}]  英[{}]".format(apiResp["basic"].get("us-phonetic"),
                                                          apiResp["basic"].get("uk-phonetic")), ""
                    item = DictResultItem(self.plugin_info, wfs, phonetic, "basic")
                    if apiResp["basic"].get("wfs"):
                        for wf in apiResp["basic"]["wfs"]:
                            wfs += "{}：{}；".format(wf["wf"]["name"], wf["wf"]["value"])
                        item.title, item.subTitle = wfs, phonetic
                    else:
                        item.title, item.subTitle = phonetic, None

                    item.action = ResultAction(play_sound, False, self.plugin_info, self.api, apiResp.get("speakUrl"))
                    results.append(item)

                if apiResp["basic"].get("explains"):
                    for exp in apiResp["basic"]["explains"]:
                        results.append(DictResultItem(self.plugin_info, exp, self.text, "translate"))
            self.sin_out.emit(self.token, results)
        except BaseException as e:
            log.error(e)


class TranslatePlugin(AbstractPlugin):
    meta_info = PluginInfo("在线词典", "使用有道云接口的在线典", "images/dict_basic.png",
                           ["dict"], True)

    def __init__(self, api: ContextApi):
        # threading.Thread(target=self.loadDict).start()
        self.localDict = {}
        self.api = api

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
                    results.append(DictResultItem(self.meta_info, translation, text, "translate"))
            return results, YoudaoApiThread(self.meta_info, parent, self.api, text, token)
        else:
            return [], None
