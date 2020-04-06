import os
import shutil
import re
from datetime import datetime

from PyQt5.QtGui import QIcon, QGuiApplication
from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface
from result_model import ResultItem, ResultAction


class SSJPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("随手记", "快速记录想法到markdown文件中，支持多文件。", "images/ssj_icon.png",
                           ["sj"], False)
    commands = ("show", "del")

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.doc_root = self.get_setting("doc_root")
        self.api = api

    def query(self, keyword, text, token=None, parent=None):
        results = []
        open_setting_action = ResultAction(os.startfile, False, self.setting_path)
        if self.doc_root is None or len(self.doc_root.strip()) == 0:
            return [
                ResultItem(self.meta_info, "请先设置文档目录，再使用插件", "点击进入设置界面", "images/ssj_error.png", open_setting_action)]
        if not os.path.isdir(self.doc_root):
            return [ResultItem(self.meta_info, "文档目录不存在", "点击设置文档目录", "images/ssj_error.png", open_setting_action)]

        match = re.match("(.*?)(:{1,2})(.*)", text)

        doc_search, tip = "", ""
        mode = ""
        if match:
            doc_search = match.groups()[0]
            mode = match.groups()[1]
            tip = match.groups()[2]
        else:
            tip = text
        doc_matchs, total_match = [], False
        if doc_search:
            for doc in os.listdir(self.doc_root):
                if doc.endswith(".md") and not os.path.isdir(doc) and str(doc[0:-3]).find(doc_search) > -1:
                    doc_matchs.append(doc)
                    if doc == doc_search + ".md":
                        total_match = True
        else:
            for doc in os.listdir(self.doc_root):
                if doc.endswith(".md") and not os.path.isdir(doc):
                    doc_matchs.append(doc)
        if mode == ":" and tip in self.commands:
            if tip == "show":
                if total_match:
                    with open(os.path.join(self.doc_root, doc_search + ".md"), "r", encoding="utf-8") as doc:
                        clipboard = QGuiApplication.clipboard()
                        for line in doc.readlines():
                            if line.strip():
                                item_match = re.match("\\[(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})] (.*)", line)
                                if item_match:
                                    action = ResultAction(clipboard.setText, True, item_match.groups()[1])
                                    results.append(
                                        ResultItem(self.meta_info, item_match.groups()[1], item_match.groups()[0],
                                                   "images/ssj_item.png",
                                                   action))
                                else:
                                    action = ResultAction(clipboard.setText, True, line)
                                    results.append(ResultItem(self.meta_info, line, "", "images/ssj_item.png", action))
                else:
                    for doc in doc_matchs:
                        action = ResultAction(self.api.change_query, False,
                                              "{} {}:{}".format(keyword, str(doc[0:-3]), tip))
                        results.append(ResultItem(self.meta_info, doc, "选择此文档查看内容", "images/ssj_choose.png", action))
            elif tip == "del":
                for doc in doc_matchs:
                    action = ResultAction(self.deleteDoc, True, doc)
                    results.append(ResultItem(self.meta_info, doc, "删除此文档", "images/ssj_delete.png", action))

        else:
            blank, multi = not bool(tip.strip()), mode == "::"
            if blank:
                if total_match and not multi:
                    for cmd in self.commands:
                        to_query = "{} {}:{}".format(keyword, str(doc_search), cmd)
                        action = ResultAction(self.api.change_query, False, to_query)
                        results.append(
                            ResultItem(self.meta_info, cmd, doc_search + ".md", "images/ssj_cmd.png", action))
                    for doc in doc_matchs:
                        if doc != doc_search + ".md":
                            to_query = "{} {}{}".format(keyword, str(doc[0:-3]), mode)
                            action = ResultAction(self.api.change_query, False, to_query)
                            results.append(ResultItem(self.meta_info, doc, "选择此文档", "images/ssj_choose.png", action))
                else:
                    if mode == "":
                        mode = ":"
                    for doc in doc_matchs:
                        to_query = "{} {}{}".format(keyword, str(doc[0:-3]), mode)
                        action = ResultAction(self.api.change_query, False, to_query)
                        results.append(ResultItem(self.meta_info, doc, "选择此文档", "images/ssj_choose.png", action))
            else:
                t_tip = (datetime.now(), tip)
                if not total_match and doc_search.strip():
                    to_query = None
                    if multi:
                        to_query = "{} {}::".format(keyword, doc_search)
                    action = ResultAction(self.appendDoc, not multi, doc_search.strip() + ".md", t_tip, to_query)
                    results.append(
                        ResultItem(self.meta_info, "新建文档：" + doc_search + ".md", tip, "images/ssj_new.png", action))

                for doc in doc_matchs:
                    to_query = None
                    if multi:
                        to_query = "{} {}::".format(keyword, doc)
                    action = ResultAction(self.appendDoc, not multi, doc, t_tip, to_query)
                    results.append(ResultItem(self.meta_info, doc, tip, "images/ssj_choose.png", action))
        return results

    def appendDoc(self, doc, t_tip, multi=None):
        with open(os.path.join(self.doc_root, doc), "a", encoding="utf-8") as file:
            file.write("[{}] {}\n\n".format(t_tip[0].strftime("%Y-%m-%d %H:%M:%S"), t_tip[1]))
        if multi:
            self.api.change_query(multi)

    def deleteDoc(self, doc):
        shutil.move(os.path.join(self.doc_root, doc),
                    os.path.join(self.doc_root, ".delete", str(int(datetime.now().timestamp())) + "-" + doc))
        self.api.show_message("随手记: 删除文档", doc, QIcon(os.path.join(self.meta_info.path, "images/ssj_delete.png")), 1000)
