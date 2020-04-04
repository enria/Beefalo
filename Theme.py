import os, json

from Plugin import AbstractPlugin
from ResultModel import ResultItem, ResultAction, ContextApi


class ThemePlugin(AbstractPlugin):
    keywords = ["theme"]
    _name_, _desc_, _icon_ = "主题", "更改主题", "theme_icon.png"

    def __init__(self, api: ContextApi):
        self.callback = False
        self.api = api
        self.themes = {}
        for theme in os.listdir("resource"):
            if theme.endswith(".css"):
                with open(os.path.join("resource", theme), "r") as theme_file:
                    lines = theme_file.readlines()
                    self.themes[str(theme[0:-4])] = (str(theme[0:-4]), "\n".join(lines[1:]), json.loads(lines[0]))

    def defaultTheme(self):
        return self.themes[self.api.get_setting("theme")]

    def query(self, keyword, text):
        results = []
        for theme in self.themes:
            action = ResultAction(self.api.change_theme, False, self.themes[theme][0], self.themes[theme][1],
                                  self.themes[theme][2])
            results.append(ResultItem(theme, "", "theme_icon.png", action))
        return results
