from math import *

from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface
from result_model import ResultItem, ResultAction


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


class CalculatorPlugin(AbstractPlugin):
    meta_info = PluginInfo("计算器", "支持math库下的函数", "images/calculator_icon.png",
                           ["*"], False)

    def __init__(self, api: ContextApi):
        self.api = api

    def query(self, keyword, text, token=None, parent=None):
        try:
            value = eval(text)
            if is_number(value):
                return [ResultItem(self.meta_info, str(value), text, "images/calculator_icon.png")]
        except BaseException as e:
            pass
        return []
