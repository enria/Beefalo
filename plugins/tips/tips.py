import os
import shutil
import re
from datetime import datetime
from pathlib import Path

from PyQt5.QtGui import QIcon

from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface
from result_model import ResultItem, ResultAction, MenuItem, CopyAction


class TipsPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("Tips", "记录想法，支持多个文件。 ", "images/ssj_icon.png",
                           ["tip"], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.doc_root = self.get_setting("doc_root")
        self.api = api

    def query(self, keyword, text, token=None, parent=None):
        results = []
        open_setting_action = ResultAction(self.api.edit_setting, False, TipsPlugin)
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
        docs=[path.name \
            for path in sorted(Path(self.doc_root).iterdir(), key=os.path.getmtime,reverse=True)\
            if not path.is_dir() and path.name.endswith(".md")]
        if doc_search:
            search_lower = doc_search.lower()
            for doc in docs:
                doc_lower = doc.lower()
                if str(doc_lower[0:-3]).find(search_lower) > -1:
                    doc_matchs.append(doc)
                    if doc_lower == search_lower + ".md":
                        total_match = True
        else:
            for doc in docs:
                doc_matchs.append(doc)
        if not tip.strip():
            if total_match:
                for doc in doc_matchs:
                    if doc.lower() != doc_search.lower() + ".md":
                        to_query = "{} {}{}".format(keyword, str(doc[0:-3]), mode)
                        action = ResultAction(self.api.change_query, False, to_query)
                        item = ResultItem(self.meta_info, doc, "选择此文档查看内容", "images/ssj_choose.png", action)
                        item.menus = [MenuItem("️ 删除", ResultAction(self.deleteDoc, doc))]
                        results.append(item)
                with open(os.path.join(self.doc_root, doc_search + ".md"), "r", encoding="utf-8") as doc:
                    for line in doc.readlines():
                        if line.strip():
                            item_match = re.match(r"\[(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})]\s(.*)", line)
                            if item_match:
                                copy_action = CopyAction(item_match.groups()[1])
                                item = ResultItem(self.meta_info, item_match.groups()[1], item_match.groups()[0],
                                                  "images/ssj_item.png")
                            else:
                                copy_action = CopyAction(line)
                                item = ResultItem(self.meta_info, line, "", "images/ssj_item.png")
                            delete_action = ResultAction(self.deleteTip, False, doc_search + ".md", line)
                            item.menus = [MenuItem(" 复制", copy_action), MenuItem("️ 删除", delete_action)]
                            results.append(item)

            else:
                for doc in doc_matchs:
                    action = ResultAction(self.api.change_query, False,
                                          "{} {}:".format(keyword, str(doc[0:-3])))
                    item = ResultItem(self.meta_info, doc, "选择此文档查看内容", "images/ssj_choose.png", action)
                    item.menus = [
                        MenuItem("️ 删除", ResultAction(self.deleteDoc, False, doc, "{} {}".format(keyword, text)))]
                    results.append(item)

        else:
            multi = mode == "::"
            t_tip = (datetime.now(), tip)
            if not total_match:
                if doc_search.strip():
                    to_query = None
                    if multi:
                        to_query = "{} {}::".format(keyword, doc_search)
                    action = ResultAction(self.appendDoc, not multi, doc_search + ".md", t_tip, to_query)
                    results.append(
                        ResultItem(self.meta_info, "新建文档：{}.md".format(doc_search), tip, "images/ssj_new.png", action))
            if not doc_matchs:
                doc_matchs = ["默认文档.md"]
            for doc in doc_matchs:
                to_query = None
                if multi:
                    to_query = "{} {}::".format(keyword, str(doc[:-3]))
                action = ResultAction(self.appendDoc, not multi, doc, t_tip, to_query)
                results.append(ResultItem(self.meta_info, doc, tip, "images/ssj_choose.png", action))

        return results

    def appendDoc(self, doc, t_tip, multi=None):
        with open(os.path.join(self.doc_root, doc), "a", encoding="utf-8") as file:
            file.write("[{}] {}\n\n".format(t_tip[0].strftime("%Y-%m-%d %H:%M:%S"), t_tip[1]))
        if multi:
            self.api.change_query(multi)

    def deleteDoc(self, doc, to_query="sj "):
        shutil.move(os.path.join(self.doc_root, doc),
                    os.path.join(self.doc_root, ".delete", str(int(datetime.now().timestamp())) + "-" + doc))
        self.api.show_message("随手记: 删除文档", doc, QIcon(os.path.join(self.meta_info.path, "images/ssj_delete.png")), 1000)
        self.api.change_query(to_query)

    def deleteTip(self, doc, tip):
        with open(os.path.join(self.doc_root, doc), "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(os.path.join(self.doc_root, doc), "w", encoding="utf-8") as file:
            new_lines = []
            for line in lines:
                if line == tip or not line.strip():
                    continue
                new_lines.append(line)
            new_lines.append("\n\n")
            file.write("\n\n".join(new_lines))

        self.api.change_query("{} {}:".format(self.meta_info.keywords[0], str(doc[:-3])))

    def reload(self):
        SettingInterface.reload(self)
        self.doc_root = self.get_setting("doc_root")
