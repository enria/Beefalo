import os
import ctypes
from ctypes.wintypes import *
import platform

from PyQt5.QtCore import QThread, pyqtSignal, QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileIconProvider

from result_model import ResultItem, ResultAction
from plugin_api import AbstractPlugin, PluginInfo, SettingInterface, ContextApi
from file_icon import file_icons


def open_file(file, plugin_info, api):
    try:
        os.startfile(file)
    except BaseException as e:
        api.show_message("无法打开文件", str(e),
                         QIcon(os.path.join(plugin_info.path, "images/everything_error.png")), 1000)


class FileResultItem(ResultItem):
    def __init__(self, plugin_info, fileName: str, fullPath, isDir, api, system_icon=False):
        super().__init__(plugin_info)
        self.title = fileName
        self.subTitle = fullPath

        if system_icon:
            provider = QFileIconProvider()
            self.icon = provider.icon(QFileInfo(fullPath))
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


class AsyncSearchThread(QThread):
    sinOut = pyqtSignal([str, list])

    def __init__(self, parent, text, token, api, plugin_info, query_max=50, system_icon=False, root=None):
        super(AsyncSearchThread, self).__init__(parent)
        self.text = text
        self.token = token
        self.api = api
        self.plugin_info = plugin_info
        self.query_max = query_max
        self.system_icon = system_icon
        self.root = root

    @staticmethod
    def getFileName(path: str):
        return path.split("\\")[-1]

    def run(self):
        try:
            results = everything_query(self.root, self.text, self.query_max, self.plugin_info, self.api,
                                       self.system_icon)
            self.sinOut.emit(self.token, results)
        except BaseException as e:
            print(e)


global everything_dll


def everything_query(root, text, query_max, plugin_info, api, system_icon):
    if root:
        everything_dll.Everything_SetSearchW(root + " " + text)
    else:
        everything_dll.Everything_SetSearchW(text)
    if query_max:
        everything_dll.Everything_SetMax(query_max)
    everything_dll.Everything_QueryW(True)
    num_results = everything_dll.Everything_GetNumResults()
    fullPath = ctypes.create_unicode_buffer(500)
    results = []
    for i in range(num_results):
        everything_dll.Everything_GetResultFullPathNameW(i, fullPath, 490)
        path = ctypes.wstring_at(fullPath)
        if system_icon:
            results.append(
                FileResultItem(plugin_info, AsyncSearchThread.getFileName(path), path, False,
                               api, True))
        else:
            results.append(
                FileResultItem(plugin_info, AsyncSearchThread.getFileName(path), path, os.path.isdir(path),
                               api))
    return results


class EverythingPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("everything", "使用Everything查找本机文件", "images/everything_search.png",
                           ["find", "*"], True)

    def __init__(self, api: ContextApi):
        super().__init__()
        self.api = api
        global everything_dll
        dll_file="Everything32.dll"
        if platform.architecture()[0].startswith("64"):
            dll_file="Everything64.dll"
        everything_dll = ctypes.WinDLL(os.path.join(self.meta_info.path, "dll", dll_file))
        everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
        everything_dll.Everything_GetResultFileNameW.argtypes = [DWORD]
        everything_dll.Everything_GetResultFileNameW.restype = ctypes.POINTER(ctypes.c_wchar)

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if text.strip():
            if keyword and keyword != "*":
                return [], AsyncSearchThread(parent, text, token, self.api, self.meta_info,
                                             self.get_setting("everything_query_max"),
                                             self.get_setting("system_icon"))
            else:
                return everything_query(self.get_setting("link_root"), text, self.get_setting("everything_query_max"),
                                        self.meta_info, self.api, self.get_setting("system_icon")), None
        return results, None
