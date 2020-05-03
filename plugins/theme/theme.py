import os
import json

from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, I18nInterface
from result_model import ResultItem, ResultAction


class Theme(object):
    def __init__(self, name, style, file):
        self.name = name
        self.style = style
        self.file = file


class ThemePlugin(AbstractPlugin, SettingInterface, I18nInterface):
    meta_info = PluginInfo(icon="images/theme_icon.png", keywords=["theme"], async_result=False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self, False)
        I18nInterface.__init__(self, api.language)
        self.api = api
        self.themes = {}
        for theme in os.listdir(os.path.join(self.meta_info.path, "resource")):
            if theme.endswith(".json"):
                with open(os.path.join(self.meta_info.path, "resource", theme), "r", encoding="utf-8") as theme_file:
                    style = json.loads(theme_file.read())
                    desc = style["desc"] if "desc" in style else theme
                    theme = str(theme[:-5])
                    self.themes[theme] = Theme(theme, style, desc)
        self.theme_template = ""
        with open(os.path.join(self.meta_info.path, "resource", "Theme.css"), "r", encoding="utf-8") as theme_file:
            self.theme_template = theme_file.read()

        theme = self.themes[self.get_setting("theme")]
        self.change_theme(theme)

    def query(self, keyword, text, token=None, parent=None):
        results = []
        for theme in self.themes:
            if text.lower() in self.themes[theme].name.lower():
                action = ResultAction(self.change_theme, False, self.themes[theme])
                results.append(
                    ResultItem(self.meta_info, theme, self.themes[theme].file, "images/theme_icon.png", action))
        return results

    def change_theme(self, theme):
        css = self.theme_template.format(mb=theme.style["background"],
                                         eb=theme.style["editor"]["background"],
                                         ec=theme.style["editor"]["color"],
                                         ebd=theme.style["editor"]["border"],
                                         rb=theme.style["result"]["background"],
                                         sb=theme.style["result"]["scroll"])
        self.api.change_theme(css, theme.style)
        self.set_setting("theme", theme.name)

    def reload(self):
        SettingInterface.reload(self)
        theme = self.themes[self.get_setting("theme")]
        self.change_theme(theme)
