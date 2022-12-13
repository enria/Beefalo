import os
import ctypes
from ctypes.wintypes import *
import platform
import subprocess
from functools import lru_cache
from pathlib import Path

import mdfind
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QFileInfo
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtWidgets import QFileIconProvider

from result_model import ResultItem, ResultAction, MenuItem, CopyAction
from plugin_api import AbstractPlugin, PluginInfo, SettingInterface, ContextApi, get_logger, I18nInterface
from utils import startfile

from subprocess import Popen, PIPE
from file_icon import file_icons

log = get_logger("Everything")


def open_file(file, plugin_info, api):
    try:
        if file.endswith(".scpt"):
            Popen(['osascript', file])
        else:
            os.system('open "%s"' % file)
    except BaseException as e:
        api.show_message("无法打开文件", str(e), QIcon(os.path.join(plugin_info.path, "images/everything_error.png")), 1000)


def to_file_path(file):
    subprocess.call(["open", "-R", file])


def copy_file(file_name):
    data = QtCore.QMimeData()
    url = QtCore.QUrl.fromLocalFile(file_name)
    data.setUrls([url])
    QGuiApplication.clipboard().setMimeData(data)


class FileResultItem(ResultItem):
    def __init__(self, plugin_info, i18n: I18nInterface, fileName: str, fullPath, isDir, api: ContextApi,
                 system_icon=False):
        super().__init__(plugin_info)
        if fileName.endswith(".lnk"):
            self.title = str(fileName[:-4])
        else:
            self.title = fileName
        self.subTitle = fullPath

        if system_icon:
            icon_file_path = fullPath
            self.icon = QFileIconProvider().icon(QFileInfo(icon_file_path))
        else:
            if isDir:
                self.icon = file_icons["folder"]
            else:
                self.icon = file_icons["*"]
                doti = fileName.rfind(".")
                if doti > -1:
                    ext = str(fileName[doti + 1:])
                    if file_icons.get(ext):
                        self.icon = file_icons[ext]
            self.icon = os.path.join("images", "icons", self.icon + ".svg")
        self.action = ResultAction(open_file, True, self.subTitle, plugin_info, api)
        self.menus = []
        if isDir:
            self.menus.append(MenuItem(" " + i18n.i18n_text("search_dir"),
                                       ResultAction(api.change_query, False,
                                                    "{} {}\\ ".format(plugin_info.keywords[0], fullPath))))
        self.menus += [
            MenuItem(" " + i18n.i18n_text("open_path"), ResultAction(to_file_path, True, self.subTitle)),
            MenuItem(" " + i18n.i18n_text("copy_file_path"), CopyAction(self.subTitle)),
            MenuItem(" " + i18n.i18n_text("copy_file"), ResultAction(copy_file, True, self.subTitle))]


class AsyncSearchThread(QThread):
    sin_out = pyqtSignal([str, list])

    def __init__(self, parent, text, token, api, plugin_info, i18n, query_max=50, system_icon=False, root=None):
        super(AsyncSearchThread, self).__init__(parent)
        self.text = text
        self.token = token
        self.api = api
        self.plugin_info = plugin_info
        self.query_max = query_max
        self.system_icon = system_icon
        self.root = root
        self.i18n = i18n

    @staticmethod
    def getFileName(path: str):
        return os.path.basename(path)

    def run(self):
        try:
            results = everything_query(self.root, self.text, self.query_max, self.plugin_info, self.i18n, self.api,
                                       self.system_icon)
            self.sin_out.emit(self.token, results)
        except BaseException as e:
            log.error(e)


global everything_dll


def everything_query(root, text, query_max, plugin_info, i18n, api, system_icon):
    args = None
    def quote(d):
        return f'{d}'
    if root:
        if type(root) == list:
            args = []
            for d in root:
                args.append("-onlyin")
                args.append(quote(os.path.expanduser(d)))
        else:
            args = ["-onlyin",quote(root)]
    else:
        args = ["-onlyin",os.path.expanduser("~")]
    if text:
        args +=["-name", text]
    else:
        args +=["-name", "kMDItemDisplayName == *"]

    num_results=mdfind.mdfind(args).strip()
    num_results=num_results.split("\n") if num_results else []
    if query_max>0:
        num_results = num_results[:query_max]
    results = []
    for path in num_results:
        if system_icon:
            results.append(
                FileResultItem(plugin_info, i18n, AsyncSearchThread.getFileName(path), path, os.path.isdir(path),
                               api, True))
        else:
            results.append(
                FileResultItem(plugin_info, i18n, AsyncSearchThread.getFileName(path), path, os.path.isdir(path),
                               api))
    return results


class MDFindPlugin(AbstractPlugin, SettingInterface, I18nInterface):
    meta_info = PluginInfo(icon="images/everything_search.png", keywords=["find"], async_result=True)

    def __init__(self, api: ContextApi):
        I18nInterface.__init__(self, api.language)
        SettingInterface.__init__(self)
        self.api = api
        self.meta_info.keywords += [x["keyword"] for x in self.get_setting("space")]

    def query(self, keyword, text, token=None, parent=None):
        if keyword == "find":
            if text.strip():
                return [], AsyncSearchThread(parent, text, token, self.api, self.meta_info, self,
                                            self.get_setting("everything_query_max"),
                                            self.get_setting("system_icon"))
        else:
            dirs =[]
            for space in self.get_setting("space"):
                if space["keyword"] == keyword:
                    dirs.extend(space["dirs"])
                    text = space.get("name","{}").format(text)
                    break
            return everything_query(dirs, text, self.get_setting("everything_query_max"),
                                    self.meta_info, self, self.api, self.get_setting("system_icon")), None
        return [], None