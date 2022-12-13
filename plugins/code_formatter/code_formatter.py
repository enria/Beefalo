import os
import re
import json
import yaml
from lxml import etree

from PyQt5.QtGui import QGuiApplication

from plugin_api import AbstractPlugin, ContextApi, PluginInfo, get_logger, I18nInterface
from result_model import ResultItem, ResultAction, CopyAction
from utils import startfile

log = get_logger("Formatter")


def convertJsTemplate(text):
    return re.sub(r"([\\`$])", r"\\\1", text)


class FormatterPlugin(AbstractPlugin, I18nInterface):
    meta_info = PluginInfo(icon="images/fmt_icon.png", keywords=["fmt"], async_result=False)

    def __init__(self, api: ContextApi):
        I18nInterface.__init__(self, api.language)
        self.api = api
        self.view = os.path.join(self.meta_info.path, "view")
        self.sqlHelper = SQLHelper()
        self.commands = {"view": self.i18n_text("cmd_view"),
                         "rmn": self.i18n_text("cmd_rmn"),
                         "adq": self.i18n_text("cmd_adq")}

    def query(self, keyword, text, token=None, parent=None):
        results = []
        clipboard = QGuiApplication.clipboard()
        clipText = clipboard.text()
        text = text.strip()
        if not clipText:
            results.append(ResultItem(self.meta_info, self.i18n_text("clipboard_blank"), "", "images/fmt_copy.png"))
            return results
        if not text:
            clipText = clipText.strip()

            if clipText.strip():
                try:
                    if clipText.startswith(("{", "[")):
                        jsonData = yaml.load(clipText, Loader=yaml.BaseLoader)
                        fmt = json.dumps(jsonData, indent=4, ensure_ascii=False)
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("copy_fmt_json"), fmt, "images/fmt_format.png",
                                       CopyAction(fmt)))
                        zipped = json.dumps(jsonData, ensure_ascii=False)
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("copy_zip_json"), zipped, "images/fmt_zip.png",
                                       CopyAction(zipped)))
                        action = ResultAction(self.openViewpage, True, "json/json.html", "json/json.js",
                                              "var jsonData=`%s`" % convertJsTemplate(fmt))
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("json_view"), self.i18n_text("use_browser"),
                                       "images/fmt_browser.png", action))
                        return results
                    elif clipText.startswith("<"):
                        dom = etree.fromstring(clipText.encode("utf-8"))  # or xml.dom.minidom.parseString(xml_string)
                        fmt = etree.tostring(dom, pretty_print=True).decode("utf-8")
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("copy_fmt_xml"), fmt, "images/fmt_format.png",
                                       CopyAction(fmt)))
                        action = ResultAction(self.openViewpage, True, "xml/xml.html", "xml/xml.js",
                                              "var xmlData=`%s`" % convertJsTemplate(fmt))
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("xml_view"), self.i18n_text("use_browser"),
                                       "images/fmt_browser.png", action))
                        return results
                    elif self.sqlHelper.isSql(clipText):
                        fmt = self.sqlHelper.format(clipText)
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("copy_fmt_sql"), fmt, "images/fmt_format.png",
                                       CopyAction(fmt)))
                        zipped = self.sqlHelper.mini(clipText)
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("copy_zip_sql"), zipped, "images/fmt_zip.png",
                                       CopyAction(zipped)))
                        action = ResultAction(self.openViewpage, True, "code/code.html", "code/code.js",
                                              "var inputLan='sql',textData=`%s`" % convertJsTemplate(fmt))
                        results.append(
                            ResultItem(self.meta_info, self.i18n_text("sql_view"), self.i18n_text("use_browser"),
                                       "images/fmt_browser.png", action))
                        return results
                except BaseException as e:
                    log.error(e)

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
                results.append(
                    ResultItem(self.meta_info, self.i18n_text("code_view"), clipText, "images/fmt_browser.png", action))
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
                action = CopyAction(fmt)
                results.append(
                    ResultItem(self.meta_info, self.i18n_text("copy_code"), fmt, "images/fmt_copy.png", action))
                action = ResultAction(self.openViewpage, True, "code/code.html", "code/code.js",
                                      "var textData=`%s`" % convertJsTemplate(fmt))
                results.append(
                    ResultItem(self.meta_info, self.i18n_text("use_browser"), fmt, "images/fmt_browser.png",
                               action))
        return results

    def openViewpage(self, page, dataFile, text):
        with open(os.path.join(self.view, dataFile), "w", encoding="utf-8") as file:
            file.write(text)
        startfile(os.path.join(self.view, page))


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
