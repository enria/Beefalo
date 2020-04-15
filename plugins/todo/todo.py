import re
import os
import uuid
from datetime import datetime

from PyQt5.QtGui import QGuiApplication
from plugin_api import PluginInfo, ContextApi, AbstractPlugin, get_logger
from result_model import ResultItem, ResultAction, MenuItem

log = get_logger("TODO")


class Todo(object):
    def __init__(self, id, check, time, text):
        self.id = id
        self.check = check
        self.time = time
        self.text = text


class TodoPlugin(AbstractPlugin):
    meta_info = PluginInfo("Todo", "Todo 列表", "images/todo_icon1.png", ["todo"], False)
    todo_file = "todo.md"

    def __init__(self, api: ContextApi):
        self.api = api
        self.pattern = r"^(.+?) \[(x?)\] \((.*?)\) (.*)"  # 123 [-] (2018) 12345

    def load_items(self, text):
        # 123 [-] (2018) 12345
        text = text.strip()
        results = []
        with open(os.path.join(self.meta_info.path, self.todo_file), "r", encoding="utf-8") as todo_list:
            for line in todo_list.readlines():
                match = re.match(self.pattern, line)
                if match:
                    groups = match.groups()
                    _id, _check, _time, _text = groups[0], groups[1] == "x", groups[2], groups[3]
                    if text in _text:
                        results.append(Todo(_id, _check, _time, _text))
        return results[::-1]

    def change_status(self, todo_id, to_query, delete=False):
        results = []
        with open(os.path.join(self.meta_info.path, self.todo_file), "r", encoding="utf-8") as todo_list:
            for line in todo_list.readlines():
                match = re.match(self.pattern, line)
                if match:
                    groups = match.groups()
                    _id, _check, _time, _text = groups[0], groups[1] == "x", groups[2], groups[3]
                    todo = Todo(_id, _check, _time, _text)
                    if _id == todo_id:
                        if delete:
                            continue
                        todo.check = not todo.check
                    results.append(todo)
        with open(os.path.join(self.meta_info.path, self.todo_file), "w", encoding="utf-8") as todo_list:
            for todo in results:
                check = "x" if todo.check else ""
                todo_list.write("{} [{}] ({}) {}\n".format(todo.id, check, todo.time, todo.text))
        self.api.change_query(to_query)

    def add_todo(self, text, to_query):
        with open(os.path.join(self.meta_info.path, self.todo_file), "a", encoding="utf-8") as todo_list:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            todo_list.write("{} [] ({}) {}\n".format(str(uuid.uuid1()), time, text))
        self.api.change_query(to_query)

    def query(self, keyword, text, token=None, parent=None):
        todos = self.load_items(text)
        results = []
        for todo in todos:
            to_query = "{} {}".format(keyword, text)
            icon = "images/todo_check1.png" if todo.check else "images/todo_todo1.png"
            action = ResultAction(self.change_status, False, todo.id, to_query)
            item = ResultItem(self.meta_info, todo.text, todo.time, icon, action)
            item.menus = [MenuItem("复制", ResultAction(QGuiApplication.clipboard().setText, True, todo.text)),
                          MenuItem("删除", ResultAction(self.change_status, False, todo.id, to_query, True))]
            results.append(item)
        if text.strip():
            to_query = "{} ".format(keyword)
            action = ResultAction(self.add_todo, False, text, to_query)
            item = ResultItem(self.meta_info, text, "新增TODO", "images/todo_add.png", action)
            results.append(item)
        return results
