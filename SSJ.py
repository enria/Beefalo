import os, shutil
import re

from PyQt5.QtGui import QIcon

from ResultModel import ResultItem, ResultAction, ContextApi
from datetime import datetime


class SSJPlugin:
    keywords = ["sj"]
    _name_, _desc_, _icon_ = "随手记", "快速记录想法到markdown文件中，支持多文件。", "ssj_icon.png"
    commands = {"show", "del"}

    def __init__(self, api: ContextApi):
        self.callback = False
        self.api = api
        self.docRoot = api.get_setting("ssj_doc_root")

    def query(self, keyword, text):
        results = []

        if self.docRoot is None or len(self.docRoot.strip()) == 0:
            return [ResultItem("请先设置文档目录，再使用插件", "点击进入设置界面", "ssj_error.png", ResultItem(None, True))]
        if not os.path.isdir(self.docRoot):
            return [ResultItem("文档目录不存在", "点击设置文档目录", "ssj_error.png", ResultItem(None, True))]

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
            for doc in os.listdir(self.docRoot):
                if doc.find(doc_search) > -1 and doc.endswith(".md") and not os.path.isdir(doc):
                    doc_matchs.append(doc)
                    if doc == doc_search + ".md":
                        total_match = True
        else:
            for doc in os.listdir(self.docRoot):
                if doc.endswith(".md") and not os.path.isdir(doc):
                    doc_matchs.append(doc)
        if mode == ":" and tip in self.commands:
            if tip == "show":
                if total_match:
                    with open(os.path.join(self.docRoot, doc_search + ".md"), "r", encoding="utf-8") as doc:
                        for line in doc.readlines():
                            if line.strip():
                                item_match = re.match("\\[(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})] (.*)", line)
                                if item_match:
                                    results.append(
                                        ResultItem(item_match.groups()[1], item_match.groups()[0], "ssj_item.png"))
                                else:
                                    results.append(ResultItem(line, "", "ssj_item.png"))
                else:
                    for doc in doc_matchs:
                        action = ResultAction(self.api.change_query, False,
                                              "{} {}:{}".format(keyword, str(doc[0:-3]), tip))
                        results.append(ResultItem(doc, "选择此文档查看内容", "ssj_choose.png", action))
            elif tip == "del":
                for doc in doc_matchs:
                    action = ResultAction(self.deleteDoc, True, doc)
                    results.append(ResultItem(doc, "删除此文档", "ssj_delete.png", action))

        else:
            blank, multi = not bool(tip.strip()), mode == "::"
            if blank:
                if total_match and not multi:
                    for cmd in self.commands:
                        to_query = "{} {}:{}".format(keyword, str(doc_search), cmd)
                        action = ResultAction(self.api.change_query, False, to_query)
                        results.append(ResultItem(cmd, doc_search + ".md", "ssj_cmd.png", action))
                    for doc in doc_matchs:
                        if doc != doc_search + ".md":
                            to_query = "{} {}{}".format(keyword, str(doc[0:-3]), mode)
                            action = ResultAction(self.api.change_query, False, to_query)
                            results.append(ResultItem(doc, "选择此文档", "ssj_choose.png", action))
                else:
                    if mode == "":
                        mode = ":"
                    for doc in doc_matchs:
                        to_query = "{} {}{}".format(keyword, str(doc[0:-3]), mode)
                        action = ResultAction(self.api.change_query, False, to_query)
                        results.append(ResultItem(doc, "选择此文档", "ssj_choose.png", action))
            else:
                t_tip = (datetime.now(), tip)
                if not total_match and doc_search.strip():
                    to_query = None
                    if multi:
                        to_query = "{} {}::".format(keyword, doc_search)
                    action = ResultAction(self.appendDoc, not multi, doc_search.strip() + ".md", t_tip, to_query)
                    results.append(ResultItem("新建文档：" + doc_search + ".md", tip, "ssj_new.png", action))

                for doc in doc_matchs:
                    to_query = None
                    if multi:
                        to_query = "{} {}::".format(keyword, doc)
                    action = ResultAction(self.appendDoc, not multi, doc, t_tip, to_query)
                    results.append(ResultItem(doc, tip, "ssj_choose.png", action))
        return results

    def appendDoc(self, doc, t_tip, multi=None):
        with open(os.path.join(self.docRoot, doc), "a", encoding="utf-8") as file:
            file.write("[{}] {}\n\n".format(t_tip[0].strftime("%Y-%m-%d %H:%M:%S"), t_tip[1]))
        if multi:
            self.api.change_query(multi)

    def deleteDoc(self, doc):
        shutil.move(os.path.join(self.docRoot, doc),
                    os.path.join(self.docRoot, ".delete", str(int(datetime.now().timestamp())) + "-" + doc))
        self.api.show_message("随手记: 删除文档", doc, QIcon("images/ssj_delete.png"), 1000)
