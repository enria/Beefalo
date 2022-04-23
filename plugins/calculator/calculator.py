from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, I18nInterface
from result_model import ResultItem, ResultAction, CopyAction
import math
from inspect import isclass
import numbers


class CalculatorPlugin(AbstractPlugin, I18nInterface):
    meta_info = PluginInfo(icon="images/calculator_icon5.png", keywords=["*"], async_result=False)

    def __init__(self, api: ContextApi):
        I18nInterface.__init__(self, api.language)
        self.api = api
        self.math_func = {'__builtins__': None}
        for attr in dir(math):
            attr_type = getattr(math, attr)
            if (callable(attr_type) or isinstance(attr_type, numbers.Number)) and not isclass(attr_type):
                self.math_func[attr] = attr_type
        self.math_func.update({"int": int, "hex": hex, "bin": bin, "oct": oct, "len": len})

    def query(self, keyword, text, token=None, parent=None):
        try:
            float(text)
            return []
        except BaseException as e:
            pass
            
        try:
            value = eval(text, self.math_func, {})
            if not callable(value):
                return [
                    ResultItem(self.meta_info, str(value), text, "images/calculator_icon5.png", CopyAction(str(value)))]
        except BaseException as e:
            pass
        return []
