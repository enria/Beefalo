# -*- coding: utf-8 -*-
import json
import sys
import uuid
import time

from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtCore import pyqtSignal, QThread, QModelIndex, QObject, QRect, QEvent
from PyQt5.QtGui import QCursor, QKeySequence, QPalette, QColor, QIcon
from PyQt5.QtWidgets import (QWidget, QApplication, QShortcut, QDesktopWidget, QLineEdit, QVBoxLayout, QListView,
                             QSizePolicy, QSystemTrayIcon, QMenu, QAction)

from Theme import ThemePlugin
from Dict import DictPlugin
from Everything import EverythingPlugin
from Formatter import FormatterPlugin
from PluginList import PluginListPlugin
from SSJ import SSJPlugin
from keyboard import Hotkey
from ResultModel import ResultItem, ResultListMode, ContextApi
from ResultListDelegate import WidgetDelegate
from WebSearch import WebSearchPlugin, AsyncSuggestThread
import ctypes
from win32process import SuspendThread, ResumeThread
import win32con
import re


class WoxWidget(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setting = None
        self.addGlobalHotkey()
        self.plugins = {}
        self.loadPlugins()
        self.initUI()

        self.installEventFilter(self)  # 把自己当成一个过滤器安装到儿子身上

        self.debounceThread = DebounceThread(self)
        self.debounceThread.sinOut.connect(self.asyncChangeResult)
        self.debounceThread.start()

        QShortcut(QKeySequence("Up"), self, self.selectedUp)
        QShortcut(QKeySequence("Down"), self, self.selectedDown)
        QShortcut(QKeySequence("Esc"), self, self.change_visible)

    def loadPlugins(self):
        api = ContextApi(self.setInputText, showMessage, self.changeTheme, self.getSetting, self.setSetting)
        plugins = [WebSearchPlugin(), EverythingPlugin(api), DictPlugin(), SSJPlugin(api), FormatterPlugin(api)]

        pluginList = PluginListPlugin(api, [WebSearchPlugin, EverythingPlugin, DictPlugin, SSJPlugin, FormatterPlugin,
                                            PluginListPlugin, ThemePlugin])
        plugins.append(pluginList)

        theme = ThemePlugin(api)
        themeName, mainTheme, highlightItem = theme.defaultTheme()
        self.delegate = WidgetDelegate(highlightItem)
        self.setStyleSheet(mainTheme)

        plugins.append(theme)
        self.plugins["*"] = []
        for pli in plugins:
            if len(pli.keywords):
                for keyword in pli.keywords:
                    if self.plugins.get(keyword):
                        self.plugins[keyword].append(pli)
                    else:
                        self.plugins[keyword] = [pli]
            else:
                self.plugins["*"].append(pli)

    def initUI(self):
        self.setGeometry(800, 66, 800, 66 + 46 * 8)
        self.setWindowTitle('Beefalo')

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setFixedHeight(66)

        vly = QVBoxLayout()

        self.ws_input = QLineEdit(self)  # 整型文本框
        font = self.ws_input.font()
        font.setFamily("微软雅黑")
        font.setPointSize(21)  # change it's size
        self.ws_input.setFont(font)
        self.ws_input.setFixedHeight(46)
        self.ws_input.setObjectName("MainLineEdit")
        self.ws_input.textChanged.connect(self.handleTextChanged)

        self.ws_input.returnPressed.connect(self.handleResultSelected)

        vly.addWidget(self.ws_input)

        self.setWindowFlag(QtCore.Qt.ToolTip)

        self.listview = QListView()
        self.result_model = ResultListMode(self)
        self.listview.setModel(self.result_model)
        self.listview.setMaximumHeight(0)
        self.listview.setItemDelegate(self.delegate)
        self.listview.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.listview.clicked.connect(self.handleResultSelected)
        self.listview.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        vly.addWidget(self.listview)
        vly.setContentsMargins(8, 10, 8, 10)
        vly.setSpacing(0)
        self.setLayout(vly)
        self.listview.setObjectName("ResultListView")
        self.setObjectName("MainWidget")
        self.show()
        self.activateWindow()

    def changeTheme(self, themeName, mainTheme, highlightItem):
        self.setStyleSheet(mainTheme)
        self.delegate.theme = highlightItem
        self.setSetting("theme", themeName)
        # self.listview.dataChanged()

    def addGlobalHotkey(self):
        self.hotKeys = Hotkey(self)
        self.hotKeys.sinOut.connect(self.change_visible)
        self.hotKeys.inputSinOut.connect(self.setInputText)
        self.hotKeys.start()

    def change_visible(self):
        if self.isVisible():
            self.setVisible(False)
            self.clear_input_result()
        else:
            self.activateWindow()
            self.setVisible(True)

    def setInputText(self, text):
        self.ws_input.setText(text)
        self.activateWindow()
        self.setVisible(True)

    def selectedUp(self):
        if self.result_model.selected:
            self.handleResultPeek(self.result_model.createIndex(self.result_model.selected - 1, 0))
        elif self.result_model.rowCount() > 1:
            self.handleResultPeek(self.result_model.createIndex(self.result_model.rowCount() - 1, 0))

    def selectedDown(self):
        if self.result_model.selected < self.result_model.rowCount() - 1:
            self.handleResultPeek(self.result_model.createIndex(self.result_model.selected + 1, 0))
        elif self.result_model.rowCount() > 1:
            self.handleResultPeek(self.result_model.createIndex(0, 0))

    def clear_input_result(self):
        self.ws_input.setText("")

    def asyncAddResults(self, token, results):
        if token == self.token:
            self.result_model.addItems(results)

    def asyncChangeResult(self, results):
        self.result_model.changeItems(results)
        self.handleResultPeek(self.result_model.createIndex(0, 0))

    def handleTextChanged(self):
        if self.debounceThread.pause:
            self.debounceThread.resume()
        self.debounceThread.work = False

    def handleMouseEnter(self, index):
        if self.mouseMove:
            self.handleResultPeek(index)

    def handleResultPeek(self, index):
        old = self.result_model.createIndex(self.result_model.selected, 0)
        self.result_model.selected = index.row()
        self.listview.dataChanged(index, old)
        self.listview.scrollTo(index)

    def handleResultSelected(self):
        if self.result_model.selected >= 0:
            index = self.result_model.data(self.result_model.createIndex(self.result_model.selected, 0))
            if index.action.close:
                self.change_visible()
            if index.action.method:
                index.action.method(*index.action.args)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            self.change_visible()
            return True  # 说明这个事件已被处理，其他控件别插手
        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理

    def getSetting(self, key):
        if not self.setting:
            self.setting = json.load(open(".config", encoding="utf-8"))
        return self.setting.get(key)

    def setSetting(self, key, value):
        if not self.setting:
            self.setting = json.load(open(".config", encoding="utf-8"))
        self.setting[key] = value
        with open(".config", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.setting, ensure_ascii=False, indent=4))


class DebounceThread(QThread):
    sinOut = pyqtSignal([list])

    def __init__(self, view):
        super(DebounceThread, self).__init__(view.thread())
        self.view = view
        self.work = False
        self.pause = True

    def run(self):
        self.obj = QObject()
        try:
            self.handle = ctypes.windll.kernel32.OpenThread(  # @UndefinedVariable
                win32con.PROCESS_ALL_ACCESS, False, int(QThread.currentThreadId()))
        except Exception as e:
            print('get thread handle failed', e)
            return
        self.suspend()
        self.work = True
        self.pause = False
        while True:
            time.sleep(0.1)
            if self.work:
                result = []
                query = self.view.ws_input.text()
                self.view.token = str(uuid.uuid1())
                if len(query.strip()):
                    pluginMath = re.match(r"(.+?)\s+(.*)", query)
                    matched_plugins = []
                    keyword, text = "", ""
                    if pluginMath:
                        groups = pluginMath.groups()
                        keyword, text = groups[0], groups[1]
                        matched_plugins = self.view.plugins.get(keyword)

                    if not matched_plugins:
                        keyword, text = "*", query
                        matched_plugins = self.view.plugins["*"]

                    if matched_plugins:
                        for pli in matched_plugins:
                            if pli.callback:
                                item, asyncThread = pli.query(keyword, text, self.view.token, self.obj)
                                result += item
                                if asyncThread:
                                    asyncThread.sinOut.connect(self.view.asyncAddResults)
                                    asyncThread.start()
                            else:
                                result += pli.query(keyword, text)
                self.sinOut.emit(result)
                self.suspend()
            else:
                self.work = True

    def suspend(self):
        self.pause = True
        SuspendThread(self.handle)

    def resume(self):
        ResumeThread(self.handle)
        self.pause = False


global tuopan


def showMessage(*args):
    tuopan.showMessage(*args)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WoxWidget(app)
    tuopan = QSystemTrayIcon(app)  # 创建托盘
    tuopan.setIcon(QIcon("images/app_search2.png"))  # 设置托盘图标
    tpMenu = QMenu()
    a1 = QAction(u'显示', app)  # 添加一级菜单动作选项(关于程序)
    a1.triggered.connect(ex.change_visible)
    a2 = QAction(u'退出', app)  # 添加一级菜单动作选项(退出程序)
    a2.triggered.connect(app.exit)
    tpMenu.addAction(a1)
    tpMenu.addAction(a2)
    tuopan.setContextMenu(tpMenu)  # 把tpMenu设定为托盘的右键菜单
    tuopan.show()  # 显示托盘

    sys.exit(app.exec_())
