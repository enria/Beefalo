import json
import os
import logging
import sys
from logging.handlers import TimedRotatingFileHandler


class ContextApi:
    def __init__(self, change_query, show_message, change_theme, plugin_types,
                 get_theme, change_results, change_selected_result, play_media, setting_plugins, language):
        self.change_query = change_query
        self.show_message = show_message
        self.change_theme = change_theme
        self.plugin_types = plugin_types
        self.get_theme = get_theme
        self.change_results = change_results
        self.change_selected_result = change_selected_result
        self.play_media = play_media
        self.setting_plugins = setting_plugins
        self.edit_setting = None
        self.language = language


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

    def __init__(self, edit=True):
        self.setting_path = os.path.join(self.meta_info.path, self.SETTING_FILE)
        self.setting = None
        self.edit = edit

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

    def reload(self):
        self.setting = None


class I18nInterface(object):
    LANGUAGE_FILE = "i18n.json"

    def __init__(self, language, init_meta_info=True):
        self.language_file_path = os.path.join(self.meta_info.path, self.LANGUAGE_FILE)
        self.language_dict = None
        self.language = language
        if init_meta_info:
            self.meta_info.name = self.i18n_text("plugin_name")
            self.meta_info.desc = self.i18n_text("plugin_desc")

    def i18n_text(self, key):
        if not self.language_dict:
            all_language_data = json.load(open(self.language_file_path, encoding="utf-8"))
            if self.language in all_language_data:
                self.language_dict = all_language_data[self.language]
            else:
                self.language_dict = next(iter(all_language_data.values()))
        return self.language_dict.get(key)


def get_logger(name) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file_handler = TimedRotatingFileHandler(filename="log/Beefalo.log", when="D", encoding="utf-8")
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logging.INFO)
    log.addHandler(log_file_handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return log
