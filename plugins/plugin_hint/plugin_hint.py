import os
import re
from plugin_api import AbstractPlugin, ContextApi, PluginInfo
from result_model import ResultItem, ResultAction


def convertJsTemplate(text):
    return re.sub(r"([\\`$])", r"\\\1", text)


class PluginHintPlugin(AbstractPlugin):
    meta_info = PluginInfo("插件提示", "补全插件关键字", "images/plugin_hint_icon.png",
                           ["pl", "*"], False)

    def __init__(self, api: ContextApi):
        self.api = api

    def getPluginItem(self, plugin: AbstractPlugin, key):
        action = ResultAction(self.api.change_query, False, key)
        subTitle = "{}（关键字: [ {} ]）".format(plugin.meta_info.desc, ", ".join(plugin.meta_info.keywords))
        return ResultItem(self.meta_info, plugin.meta_info.name, subTitle,
                          os.path.join(plugin.meta_info.path, plugin.meta_info.icon),
                          action, True)

    def query(self, keyword, text):
        results = []
        if keyword and keyword != "*":
            for plugin in self.api.plugin_types:
                key = ""
                if plugin.meta_info.keywords and plugin.meta_info.keywords[0] != "*":
                    key = plugin.meta_info.keywords[0] + " "
                results.append(self.getPluginItem(plugin, key))
        else:
            for plugin in self.api.plugin_types:
                for key in plugin.meta_info.keywords:
                    if key.startswith(text):
                        results.append(self.getPluginItem(plugin, key + " "))
                        break
        return results
