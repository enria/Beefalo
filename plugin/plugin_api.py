import json
import os


class ContextApi:
    def __init__(self, change_query, show_message, change_theme, plugin_types, main_window, get_theme, change_results):
        self.change_query = change_query
        self.show_message = show_message
        self.change_theme = change_theme
        self.plugin_types = plugin_types
        self.main_window = main_window
        self.get_theme = get_theme
        self.change_results = change_results


class PluginInfo(object):
    def __init__(self, name=None, desc=None, icon=None, keywords=None, async_result=False):
        self.name = name
        self.icon = icon
        self.desc = desc
        self.keywords = keywords
        self.async_result = async_result
        self.path = None


class AbstractPlugin(object):
    meta_info = PluginInfo()

    def query(self, keyword, text, token=None, parent_object=None):
        pass


class SettingInterface(object):
    SETTING_FILE = "setting.json"

    def __init__(self):
        self.setting_path = os.path.join(self.meta_info.path, self.SETTING_FILE)
        self.setting = None

    def get_setting(self, key):
        if not self.setting:
            self.setting = json.load(open(self.setting_path, encoding="utf-8"))
        return self.setting.get(key)

    def set_setting(self, key, value):
        if not self.setting:
            self.setting = json.load(open(self.setting_path, encoding="utf-8"))
        self.setting[key] = value
        with open(self.setting_path, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.setting, ensure_ascii=False, indent=4))
