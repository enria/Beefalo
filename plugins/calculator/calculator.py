from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface
from result_model import ResultItem, ResultAction
import math
from inspect import isclass
import numbers


class CalculatorPlugin(AbstractPlugin):
    meta_info = PluginInfo("计算器", "支持math库下的函数", "images/calculator_icon5.png",
                           ["*"], False)

    def __init__(self, api: ContextApi):
        self.api = api
        self.math_func = {'__builtins__': None}
        for attr in dir(math):
            attr_type = getattr(math, attr)
            if (callable(attr_type) or isinstance(attr_type, numbers.Number)) and not isclass(attr_type):
                self.math_func[attr] = attr_type
        self.math_func.update({"int": int, "hex": hex, "bin": bin, "oct": oct})

    def query(self, keyword, text, token=None, parent=None):
        try:
            value = eval(text, self.math_func, {})
            if not callable(value):
                return [ResultItem(self.meta_info, str(value), text, "images/calculator_icon5.png")]
        except:
            pass
        return []
