import os
import ctypes
from ctypes.wintypes import *
import platform
import subprocess
from functools import lru_cache
from pathlib import Path
import win32com.client
import pythoncom

import win32gui
import win32ui

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QFileInfo
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtWidgets import QFileIconProvider
from PyQt5.QtWinExtras import QtWin

from result_model import ResultItem, ResultAction, MenuItem, CopyAction
from plugin_api import AbstractPlugin, PluginInfo, SettingInterface, ContextApi, get_logger, I18nInterface
from file_icon import file_icons

log = get_logger("Everything")


def open_file(file, plugin_info, api):
    try:
        os.startfile(file)
    except BaseException as e:
        api.show_message("无法打开文件", str(e),
                         QIcon(os.path.join(plugin_info.path, "images/everything_error.png")), 1000)


def to_file_path(file):
    subprocess.Popen(r'explorer /select,' + file)


def copy_file(file_name):
    data = QtCore.QMimeData()
    url = QtCore.QUrl.fromLocalFile(file_name)
    data.setUrls([url])
    QGuiApplication.clipboard().setMimeData(data)


@lru_cache(maxsize=512)
def get_link_target(link_file):
    ws = win32com.client.Dispatch("wscript.shell")
    shortcut = ws.CreateShortcut(link_file)
    # print(scut.iconlocation,"========",scut.TargetPath)
    # if scut.TargetPath:
    #     return QFileIconProvider().icon(QFileInfo(scut.TargetPath))
    # return os.path.join("images", "icons", file_icons.get("lnk") + ".svg")

    iconPath, iconId = shortcut.iconLocation.split(',')
    iconId = int(iconId)
    if not iconPath:
        iconPath = shortcut.targetPath
    iconPath = os.path.expandvars(iconPath)
    if not iconId:
        return QIcon(QFileIconProvider().icon(QFileInfo(iconPath)))

    iconRes = win32gui.ExtractIconEx(iconPath, iconId)
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()
    # I think there's a way to find available icon sizes, I'll leave it up to you
    hbmp.CreateCompatibleBitmap(hdc,64,64)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    hdc.DrawIcon((0, 0), iconRes[0][0])
    hdc.DeleteDC()
    # the original QtGui.QPixmap.fromWinHBITMAP is now part of the
    # QtWin sub-module
    return QIcon(QtWin.fromHBITMAP(hbmp.GetHandle(), 2))


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

            if fileName.endswith(".url"):
                self.icon = os.path.join("images", "icons", file_icons.get("url") + ".svg")
            else:
                icon_file_path = fullPath
                if fileName.endswith(".lnk"):
                    self.icon = get_link_target(fullPath)
                else:
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
        pythoncom.CoInitialize()
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
        return path.split("\\")[-1]

    def run(self):
        try:
            results = everything_query(self.root, self.text, self.query_max, self.plugin_info, self.i18n, self.api,
                                       self.system_icon)
            self.sin_out.emit(self.token, results)
        except BaseException as e:
            log.error(e)


global everything_dll


def everything_query(root, text, query_max, plugin_info, i18n, api, system_icon):
    if root:
        root_path = "|".join(["<{}>".format(path) for path in root])
        everything_dll.Everything_SetSearchW(root_path + " " + text)
    else:
        everything_dll.Everything_SetSearchW(text)
    if query_max:
        everything_dll.Everything_SetMax(query_max)
    everything_dll.Everything_QueryW(True)
    # everything_dll.Everything_SetMatchPath(True)
    # everything_dll.Everything_SetRegex(True)
    num_results = everything_dll.Everything_GetNumResults()
    fullPath = ctypes.create_unicode_buffer(500)
    results = []
    for i in range(num_results):
        everything_dll.Everything_GetResultFullPathNameW(i, fullPath, 490)
        path = ctypes.wstring_at(fullPath)
        if system_icon:
            results.append(
                FileResultItem(plugin_info, i18n, AsyncSearchThread.getFileName(path), path, os.path.isdir(path),
                               api, True))
        else:
            results.append(
                FileResultItem(plugin_info, i18n, AsyncSearchThread.getFileName(path), path, os.path.isdir(path),
                               api))
    return results


class EverythingPlugin(AbstractPlugin, SettingInterface, I18nInterface):
    meta_info = PluginInfo(icon="images/everything_search.png", keywords=["find", "*"], async_result=True)

    def __init__(self, api: ContextApi):
        I18nInterface.__init__(self, api.language)
        SettingInterface.__init__(self)
        self.api = api
        global everything_dll
        dll_file = "Everything32.dll"
        if platform.architecture()[0].startswith("64"):
            dll_file = "Everything64.dll"
        everything_dll = ctypes.WinDLL(os.path.join
                                       (self.meta_info.path, "dll", dll_file))
        everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
        everything_dll.Everything_GetResultFileNameW.argtypes = [DWORD]
        everything_dll.Everything_GetResultFileNameW.restype = ctypes.POINTER(ctypes.c_wchar)

    def query(self, keyword, text, token=None, parent=None):
        pythoncom.CoInitialize()  # wscript.shell
        if text.strip():
            if keyword and keyword != "*":
                return [], AsyncSearchThread(parent, text, token, self.api, self.meta_info, self,
                                             self.get_setting("everything_query_max"),
                                             self.get_setting("system_icon"))
            else:
                return everything_query(self.get_setting("link_root"), text, self.get_setting("everything_query_max"),
                                        self.meta_info, self, self.api, self.get_setting("system_icon")), None
        else:
            results = []
            recent_dir = os.path.join(str(Path.home()), "AppData/Roaming/Microsoft/Windows/Recent")
            paths = sorted(Path(recent_dir).iterdir(), key=os.path.getctime, reverse=True)
            if self.get_setting("everything_query_max"):
                paths = paths[:self.get_setting("everything_query_max")]
            for item in paths:
                results.append(FileResultItem(self.meta_info, self, item.name, str(item), False, self.api,
                                              self.get_setting("system_icon")))
            return results, None
