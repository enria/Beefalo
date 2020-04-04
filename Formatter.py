import os, shutil
import re, json
import yaml
from lxml import etree
from PyQt5.QtGui import QIcon, QGuiApplication

from Plugin import AbstractPlugin
from ResultModel import ResultItem, ResultAction, ContextApi


def convertJsTemplate(text):
    return re.sub(r"([\\`$])", r"\\\1", text)


class FormatterPlugin(AbstractPlugin):
    keywords = ["fmt"]
    _name_, _desc_, _icon_ = "Formatter", "美化剪切板中的代码", "fmt_appicon.png"
    commands = {"view": "显示剪切板文本", "rmn": "删除换行", "adq": "添加引号"}

    def __init__(self, api: ContextApi):
        self.callback = False
        self.api = api
        self.view = "resource"
        self.sqlHelper = SQLHelper()

    def query(self, keyword, text):
        results = []
        clipboard = QGuiApplication.clipboard()
        clipText = clipboard.text()
        text = text.strip()
        if not clipText:
            results.append(ResultItem("剪切板为空", "", "fmt_copy.png"))
            return results;
        if not text:
            clipText = clipText.strip()

            if clipText.strip():
                try:
                    if clipText.startswith(("{", "[")):
                        jsonData = yaml.load(clipText, Loader=yaml.BaseLoader)
                        fmt = json.dumps(jsonData, indent=4, ensure_ascii=False)
                        results.append(ResultItem("复制格式化后的JSON文本", fmt, "fmt_format.png",
                                                  ResultAction(clipboard.setText, True, fmt)))
                        zipped = json.dumps(jsonData, ensure_ascii=False)
                        results.append(ResultItem("复制压缩后的JSON文本", zipped, "fmt_zip.png",
                                                  ResultAction(clipboard.setText, True, zipped)))
                        action = ResultAction(self.openViewpage, True, "view/json/json.html", "view/json/json.js",
                                              "var jsonData=`%s`" % convertJsTemplate(fmt))
                        results.append(ResultItem("在JSON视图中打开", "使用默认浏览器", "fmt_browser.png", action))
                        return results
                    elif clipText.startswith("<"):
                        dom = etree.fromstring(clipText.encode("utf-8"))  # or xml.dom.minidom.parseString(xml_string)
                        fmt = etree.tostring(dom, pretty_print=True).decode("utf-8")
                        results.append(ResultItem("复制格式化后的XML文本", fmt, "fmt_format.png",
                                                  ResultAction(clipboard.setText, True, fmt)))
                        action = ResultAction(self.openViewpage, True, "view/xml/xml.html", "view/xml/xml.js",
                                              "var xmlData=`%s`" % convertJsTemplate(fmt))
                        results.append(ResultItem("在浏览器中查看XML结构", "使用默认浏览器", "fmt_browser.png", action))
                        return results
                    elif self.sqlHelper.isSql(clipText):
                        fmt = self.sqlHelper.format(clipText)
                        results.append(ResultItem("复制格式化后的SQL", fmt, "fmt_format.png",
                                                  ResultAction(clipboard.setText, True, fmt)))
                        zipped = self.sqlHelper.mini(clipText)
                        results.append(ResultItem("复制压缩后的SQL", zipped, "fmt_zip.png",
                                                  ResultAction(clipboard.setText, True, zipped)))
                        action = ResultAction(self.openViewpage, True, "view/code/code.html", "view/code/code.js",
                                              "var inputLan='sql',textData=`%s`" % convertJsTemplate(fmt))
                        results.append(ResultItem("在浏览器中查看SQL", "使用默认浏览器", "fmt_browser.png", action))
                        return results
                except BaseException as e:
                    print(e)

            for cmd in self.commands:
                action = ResultAction(self.api.change_query, False, "%s %s" % (keyword, cmd))
                if cmd == "view":
                    results.append(ResultItem(cmd, clipText, "fmt_cmd.png", action))
                else:
                    results.append(ResultItem(cmd, self.commands[cmd], "fmt_cmd.png", action))
            return results
        else:
            fmt, cmddesc = None, self.commands.get(text)
            if text == "rmn":
                fmt = re.sub("\n", " ", clipText)
            elif text == "adq":
                fmt = '"' + re.sub("\n", "\"+\n\"", clipText) + '"'
            elif text == "view":
                action = ResultAction(self.openViewpage, True, "view/code/code.html", "view/code/code.js",
                                      "var textData=`%s`" % convertJsTemplate(clipText))
                results.append(ResultItem("在代码视图中打开", clipText, "fmt_browser.png", action))
                # TODO json sql
            else:
                for cmd in self.commands:
                    action = ResultAction(self.api.change_query, False, "%s %s" % (keyword, cmd))
                    if cmd == "view":
                        results.append(ResultItem(cmd, clipText, "fmt_cmd.png", action))
                    else:
                        results.append(ResultItem(cmd, self.commands[cmd], "fmt_cmd.png", action))

            if fmt:
                action = ResultAction(clipboard.setText, True, fmt)
                results.append(ResultItem("复制%s后的文本" % cmddesc, fmt, "fmt_copy.png", action))
                action = ResultAction(self.openViewpage, True, "view/code/code.html", "view/code/code.js",
                                      "var textData=`%s`" % convertJsTemplate(fmt))
                results.append(ResultItem("在浏览器中查看%s后的文本" % cmddesc, fmt, "fmt_browser.png", action))
        return results

    def openViewpage(self, page, dataFile, text):
        with open(os.path.join(self.view, dataFile), "w", encoding="utf-8") as file:
            file.write(text)
        os.startfile(os.path.join(self.view, page))


class SQLHelper:
    fts = {"select", "update", "insert", "delete", "drop", "create", "alter"};
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
        text = re.sub(r"([\(\),])", " \1 ", text)
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

    def mini(self, text):
        text = re.sub(r"\s*,", ", ", text)
        text = re.sub(r"\n", " ", text)
        return re.sub(r"\s{2,}", " ", text)


if __name__ == '__main__':
    print(convertJsTemplate("```\\fdsafsda$$`"))
