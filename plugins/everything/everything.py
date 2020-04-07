import os
import ctypes
from ctypes.wintypes import *

from PyQt5.QtCore import QThread, pyqtSignal, QFileInfo
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileIconProvider

from result_model import ResultItem, ResultAction
from plugin_api import AbstractPlugin, PluginInfo, SettingInterface, ContextApi
from file_icon import file_icons

EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100
EVERYTHING_REQUEST_FILE_LIST_FILE_NAME = 0x00000200
EVERYTHING_REQUEST_RUN_COUNT = 0x00000400
EVERYTHING_REQUEST_DATE_RUN = 0x00000800
EVERYTHING_REQUEST_DATE_RECENTLY_CHANGED = 0x00001000
EVERYTHING_REQUEST_HIGHLIGHTED_FILE_NAME = 0x00002000
EVERYTHING_REQUEST_HIGHLIGHTED_PATH = 0x00004000
EVERYTHING_REQUEST_HIGHLIGHTED_FULL_PATH_AND_FILE_NAME = 0x00008000

EVERYTHING_SORT_NAME_ASCENDING = 1
EVERYTHING_SORT_NAME_DESCENDING = 2


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

    def __init__(self, parent, text, token, api, plugin_info, query_max=50, system_icon=False):
        super(AsyncSearchThread, self).__init__(parent)
        self.text = text
        self.token = token
        self.api = api
        self.plugin_info = plugin_info
        self.query_max = query_max
        self.system_icon = system_icon

    @staticmethod
    def getFileName(path: str):
        return path.split("\\")[-1]

    def run(self):
        try:
            everything_dll.Everything_SetSearchW(self.text)
            if self.query_max:
                everything_dll.Everything_SetMax(self.query_max)
            everything_dll.Everything_QueryW(True)
            num_results = everything_dll.Everything_GetNumResults()
            fullPath = ctypes.create_unicode_buffer(500)
            results = []
            for i in range(num_results):
                everything_dll.Everything_GetResultFullPathNameW(i, fullPath, 490)
                path = ctypes.wstring_at(fullPath)
                if self.system_icon:
                    results.append(
                        FileResultItem(self.plugin_info, AsyncSearchThread.getFileName(path), path, False,
                                       self.api, True))
                else:
                    results.append(
                        FileResultItem(self.plugin_info, AsyncSearchThread.getFileName(path), path, os.path.isdir(path),
                                       self.api))
            self.sinOut.emit(self.token, results)
        except BaseException as e:
            print(e)


global everything_dll


class EverythingPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("everything", "使用Everything查找本机文件", "images/everything_search.png",
                           ["*"], True)

    def __init__(self, api: ContextApi):
        super().__init__()
        self.api = api
        global everything_dll
        everything_dll = ctypes.WinDLL(os.path.join(self.meta_info.path, "dll", "Everything64.dll"))
        everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
        everything_dll.Everything_GetResultFileNameW.argtypes = [DWORD]
        everything_dll.Everything_GetResultFileNameW.restype = ctypes.POINTER(ctypes.c_wchar)

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if token:
            return [], AsyncSearchThread(parent, text, token, self.api, self.meta_info,
                                         self.get_setting("everything_query_max"),
                                         self.get_setting("system_icon"))
        return results
