import ctypes
from PyQt5.QtCore import QThread, pyqtSignal
import os
from ctypes.wintypes import *

from FileIcon import fileicons
from ResultModel import ResultItem, ResultAction

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

everything_dll = ctypes.WinDLL("dll/Everything64.dll")
everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]

everything_dll.Everything_GetResultFileNameW.argtypes = [DWORD]
everything_dll.Everything_GetResultFileNameW.restype = ctypes.POINTER(ctypes.c_wchar)


class FileResultItem(ResultItem):
    from FileIcon import fileicons

    def __init__(self, fileName: str, fullPath, isDir):
        super().__init__()
        self.title = fileName
        self.subTitle = fullPath

        if isDir:
            self.icon = fileicons["folder"]
        else:
            self.icon = fileicons["*"]
            doti = fileName.rfind(".")
            if doti > -1:
                ext = str(fileName[doti + 1:])
                if fileicons.get(ext):
                    self.icon = fileicons[ext]

        self.icon = "icons/" + self.icon + ".svg"
        self.action = ResultAction(self.openFile, True)

    def openFile(self):
        os.startfile(self.subTitle)


class AsyncSearchThread(QThread):
    sinOut = pyqtSignal([str, list])

    def __init__(self, parent, text, token):
        super(AsyncSearchThread, self).__init__(parent)
        self.text = text
        self.token = token

    @staticmethod
    def getFileName(path: str):
        return path.split("\\")[-1]

    def run(self):
        try:
            everything_dll.Everything_SetSearchW(self.text)
            everything_dll.Everything_SetRequestFlags(
                EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH)
            everything_dll.Everything_SetMax(20)
            everything_dll.Everything_QueryW(True)
            num_results = everything_dll.Everything_GetNumResults()
            fullPath = ctypes.create_unicode_buffer(500)
            results = []
            for i in range(num_results):
                everything_dll.Everything_GetResultFullPathNameW(i, fullPath, 260)
                path = ctypes.wstring_at(fullPath)
                results.append(FileResultItem(AsyncSearchThread.getFileName(path), path, os.path.isdir(path)))
            self.sinOut.emit(self.token, results)
        except BaseException as e:
            print(e)


class EverythingPlugin:
    keywords = {"*"}

    def __init__(self):
        self.callback = True

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if token:
            return [], AsyncSearchThread(parent, text, token)
        return results
