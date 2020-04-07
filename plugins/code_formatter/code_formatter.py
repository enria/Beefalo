import os
import re
import json
import yaml
from lxml import etree

from PyQt5.QtGui import QGuiApplication

from plugin_api import AbstractPlugin, ContextApi, PluginInfo
from result_model import ResultItem, ResultAction


def convertJsTemplate(text):
    return re.sub(r"([\\`$])", r"\\\1", text)


class FormatterPlugin(AbstractPlugin):
    commands = {"view": "显示剪切板文本", "rmn": "删除换行", "adq": "添加引号"}

    meta_info = PluginInfo("Formatter", "美化剪切板中的代码", "images/fmt_icon.png",
                           ["fmt"], False)

    def __init__(self, api: ContextApi):
        self.api = api
        self.view = os.path.join(self.meta_info.path, "view")
        self.sqlHelper = SQLHelper()

    def query(self, keyword, text, token=None, parent=None):
        results = []
        clipboard = QGuiApplication.clipboard()
        clipText = clipboard.text()
        text = text.strip()
        if not clipText:
            results.append(ResultItem(self.meta_info, "剪切板为空", "", "images/fmt_copy.png"))
            return results
        if not text:
            clipText = clipText.strip()

            if clipText.strip():
                try:
                    if clipText.startswith(("{", "[")):
                        jsonData = yaml.load(clipText, Loader=yaml.BaseLoader)
                        fmt = json.dumps(jsonData, indent=4, ensure_ascii=False)
                        results.append(ResultItem(self.meta_info, "复制格式化后的JSON文本", fmt, "images/fmt_format.png",
                                                  ResultAction(clipboard.setText, True, fmt)))
                        zipped = json.dumps(jsonData, ensure_ascii=False)
                        results.append(ResultItem(self.meta_info, "复制压缩后的JSON文本", zipped, "images/fmt_zip.png",
                                                  ResultAction(clipboard.setText, True, zipped)))
                        action = ResultAction(self.openViewpage, True, "json/json.html", "json/json.js",
                                              "var jsonData=`%s`" % convertJsTemplate(fmt))
                        results.append(
                            ResultItem(self.meta_info, "在JSON视图中打开", "使用默认浏览器", "images/fmt_browser.png", action))
                        return results
                    elif clipText.startswith("<"):
                        dom = etree.fromstring(clipText.encode("utf-8"))  # or xml.dom.minidom.parseString(xml_string)
                        fmt = etree.tostring(dom, pretty_print=True).decode("utf-8")
                        results.append(ResultItem(self.meta_info, "复制格式化后的XML文本", fmt, "images/fmt_format.png",
                                                  ResultAction(clipboard.setText, True, fmt)))
                        action = ResultAction(self.openViewpage, True, "xml/xml.html", "xml/xml.js",
                                              "var xmlData=`%s`" % convertJsTemplate(fmt))
                        results.append(
                            ResultItem(self.meta_info, "在浏览器中查看XML结构", "使用默认浏览器", "images/fmt_browser.png", action))
                        return results
                    elif self.sqlHelper.isSql(clipText):
                        fmt = self.sqlHelper.format(clipText)
                        results.append(ResultItem(self.meta_info, "复制格式化后的SQL", fmt, "images/fmt_format.png",
                                                  ResultAction(clipboard.setText, True, fmt)))
                        zipped = self.sqlHelper.mini(clipText)
                        results.append(ResultItem(self.meta_info, "复制压缩后的SQL", zipped, "images/fmt_zip.png",
                                                  ResultAction(clipboard.setText, True, zipped)))
                        action = ResultAction(self.openViewpage, True, "code/code.html", "code/code.js",
                                              "var inputLan='sql',textData=`%s`" % convertJsTemplate(fmt))
                        results.append(
                            ResultItem(self.meta_info, "在浏览器中查看SQL", "使用默认浏览器", "images/fmt_browser.png", action))
                        return results
                except BaseException as e:
                    print(e)

            for cmd in self.commands:
                action = ResultAction(self.api.change_query, False, "%s %s" % (keyword, cmd))
                if cmd == "view":
                    results.append(ResultItem(self.meta_info, cmd, clipText, "images/fmt_cmd.png", action))
                else:
                    results.append(ResultItem(self.meta_info, cmd, self.commands[cmd], "images/fmt_cmd.png", action))
            return results
        else:
            fmt, cmd_desc = None, self.commands.get(text)
            if text == "rmn":
                fmt = re.sub("\n", " ", clipText)
            elif text == "adq":
                fmt = '"' + re.sub("\n", "\"+\n\"", clipText) + '"'
            elif text == "view":
                action = ResultAction(self.openViewpage, True, "code/code.html", "code/code.js",
                                      "var textData=`%s`" % convertJsTemplate(clipText))
                results.append(ResultItem(self.meta_info, "在代码视图中打开", clipText, "images/fmt_browser.png", action))
                # TODO json sql
            else:
                for cmd in self.commands:
                    action = ResultAction(self.api.change_query, False, "%s %s" % (keyword, cmd))
                    if cmd == "view":
                        results.append(ResultItem(self.meta_info, cmd, clipText, "images/fmt_cmd.png", action))
                    else:
                        results.append(
                            ResultItem(self.meta_info, cmd, self.commands[cmd], "images/fmt_cmd.png", action))

            if fmt:
                action = ResultAction(clipboard.setText, True, fmt)
                results.append(ResultItem(self.meta_info, "复制%s后的文本" % cmd_desc, fmt, "images/fmt_copy.png", action))
                action = ResultAction(self.openViewpage, True, "code/code.html", "code/code.js",
                                      "var textData=`%s`" % convertJsTemplate(fmt))
                results.append(
                    ResultItem(self.meta_info, "在浏览器中查看%s后的文本" % cmd_desc, fmt, "images/fmt_browser.png", action))
        return results

    def openViewpage(self, page, dataFile, text):
        with open(os.path.join(self.view, dataFile), "w", encoding="utf-8") as file:
            file.write(text)
        os.startfile(os.path.join(self.view, page))


class SQLHelper:
    fts = {"select", "update", "insert", "delete", "drop", "create", "alter"}
    tks = {"from", "left", "right", "inner", "on", "where", "group", "union", "order"}
    keepTokens, features = fts.union(tks), fts

    def isSql(self, text):
        split = re.search(r"\W", text)
        if split and split.start() > 0:
            ft = str(text[0:split.start()])
            if ft.lower() in self.fts:
                return True
        return False

    def format(self, text):
        text = re.sub(r"([(),])", " \1 ", text)
        text = re.sub("\n", " ", text)
        tokens = re.split(r"\s+", text)
        result = ""
        level, line, preSpace = 1, 0, True
        for token in tokens:
            if token.lower() in self.keepTokens:
                if line != 0:
                    result += "\n"
                line += 1
                result += " " * 4 * (level - 1) + token
            else:
                if token == "(":
                    level += 1
                    result += " " + token
                    preSpace = False
                elif token == ")":
                    level -= 1
                    result += token
                    preSpace = False
                elif token == ",":
                    result += token
                    preSpace = True
                else:
                    if preSpace:
                        result += " "
                    result += token
                    preSpace = True
        return result

    @staticmethod
    def mini(text):
        text = re.sub(r"\s*,", ", ", text)
        text = re.sub(r"\n", " ", text)
        return re.sub(r"\s{2,}", " ", text)


if __name__ == '__main__':
    print(convertJsTemplate("```\\fdsafsda$$`"))
