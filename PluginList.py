import os, shutil
import re, json
import yaml
from lxml import etree
from PyQt5.QtGui import QIcon, QGuiApplication

from Plugin import AbstractPlugin
from ResultModel import ResultItem, ResultAction, ContextApi


def convertJsTemplate(text):
    return re.sub(r"([\\`$])", r"\\\1", text)


class PluginListPlugin(AbstractPlugin):
    keywords = ["*", "pl"]
    _name_, _desc_, _icon_ = "插件提示", "补全插件关键字", "plugin_icon.png"

    def __init__(self, api: ContextApi, plugins):
        self.callback = False
        self.api = api
        self.plugins = plugins

    def getPluginItem(self, pli, key):
        action = ResultAction(self.api.change_query, False, key)
        subTitle = "{}（关键字: [ {} ]）".format(pli._desc_,", ".join(pli.keywords))
        return ResultItem(pli._name_, subTitle, pli._icon_, action)

    def query(self, keyword, text):
        results = []
        if keyword and keyword != "*":
            for pli in self.plugins:
                key = ""
                if pli.keywords and pli.keywords[0] != "*":
                    key = pli.keywords[0] + " "
                results.append(self.getPluginItem(pli, key))
        else:
            for pli in self.plugins:
                for key in pli.keywords:
                    if key.startswith(text):
                        results.append(self.getPluginItem(pli, key + " "))
                        break
        return results
