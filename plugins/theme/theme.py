import os
import json

from plugin_api import PluginInfo, SettingInterface

from plugin_api import AbstractPlugin, ContextApi
from result_model import ResultItem, ResultAction


class Theme(object):
    def __init__(self, name, main_theme, highlight_theme):
        self.name = name
        self.main_theme = main_theme
        self.highlight_theme = highlight_theme


class ThemePlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("主题", "更改主题", "images/theme_icon.png",
                           ["theme"], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.themes = {}
        for theme in os.listdir(os.path.join(self.meta_info.path, "resource")):
            if theme.endswith(".css"):
                with open(os.path.join(self.meta_info.path, "resource", theme), "r") as theme_file:
                    theme = str(theme[0:-4])
                    lines = theme_file.readlines()
                    self.themes[theme] = Theme(theme, "\n".join(lines[1:]), json.loads(lines[0]))

        theme = self.themes[self.get_setting("theme")]
        self.api.change_theme(theme.main_theme, theme.highlight_theme)

    def query(self, keyword, text, token=None, parent=None):
        results = []
        for theme in self.themes:
            action = ResultAction(self.change_theme, False, self.themes[theme])
            results.append(ResultItem(self.meta_info, theme, "", "images/theme_icon.png", action))
        return results

    def change_theme(self, theme):
        self.api.change_theme(theme.main_theme, theme.highlight_theme)
        self.set_setting("theme", theme.name)
