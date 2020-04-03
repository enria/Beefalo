# -*- coding: utf-8 -*-
import sys
import uuid
import time

from PyQt5 import QtCore, Qt, QtGui
from PyQt5.QtCore import pyqtSignal, QThread, QModelIndex, QObject, QRect
from PyQt5.QtGui import QCursor, QKeySequence, QPalette, QColor, QIcon
from PyQt5.QtWidgets import (QWidget, QApplication, QShortcut, QDesktopWidget, QLineEdit, QVBoxLayout, QListView,
                             QSizePolicy, QSystemTrayIcon, QMenu, QAction)

from Dict import DictPlugin
from Everything import EverythingPlugin
from keyboard import Hotkey
from ResultModel import ResultItem, ResultListMode
from ResultListDelegate import WidgetDelegate
from WebSearch import WebSearchPlugin, AsyncSuggestThread
import ctypes
from win32process import SuspendThread, ResumeThread
import win32con
import re


class WoxWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.addGlobalHotkey()
        self.plugins = {}
        self.loadPlugins()

        self.debounceThread = DebounceThread(self)
        self.debounceThread.sinOut.connect(self.asyncChangeResult)
        self.debounceThread.start()

        QShortcut(QKeySequence("Up"), self, self.selectedUp)
        QShortcut(QKeySequence("Down"), self, self.selectedDown)
        QShortcut(QKeySequence("Esc"), self, self.change_visible)

    def loadPlugins(self):
        plugins = [WebSearchPlugin(), EverythingPlugin(), DictPlugin()]
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
        self.setWindowTitle('Burning widget')

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
        self.ws_input.setStyleSheet("color:#e3e0e3;background-color:#616161;border:0;padding:3px 0;margin:0px;")
        self.ws_input.setFixedHeight(46)
        self.ws_input.textChanged.connect(self.handleTextChanged)

        self.ws_input.returnPressed.connect(self.handleResultSelected)

        vly.addWidget(self.ws_input)

        self.setWindowFlag(QtCore.Qt.ToolTip)
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.listview = QListView()
        self.result_model = ResultListMode(self)
        self.listview.setModel(self.result_model)
        self.listview.setMaximumHeight(0)
        self.listview.verticalScrollBar().setStyleSheet("""
        QScrollBar:vertical
        {
            width:6px;
            background:rgba(0,0,0,0%);
            margin:0;
            padding-top:0px;   
            padding-bottom:0px;
        }
        QScrollBar::handle:vertical
        {
            width:6px;
            background:#616161;
            border-radius:3px;  
            min-height:10px;
        }
        QScrollBar::add-line:vertical   
        {
            height:0px;width:0px;
        }
        QScrollBar::sub-line:vertical   
        {
            height:0px;width:0px;
        }
        QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical 
        {
            background:rgba(0,0,0,0%);
            border-radius:4px;
        }""")
        self.listview.setItemDelegate(WidgetDelegate())
        self.listview.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.listview.clicked.connect(self.handleResultSelected)
        self.listview.entered.connect(self.handleResultPeek)
        self.listview.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.listview.setMouseTracking(True)

        vly.addWidget(self.listview)
        vly.setContentsMargins(8, 10, 8, 10)
        vly.setSpacing(0)
        self.setLayout(vly)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#424242"))
        palette.setColor(QPalette.Base, QColor("#424242"))
        palette.setColor(QPalette.AlternateBase, QColor("#424242"))
        self.listview.setPalette(palette)
        self.listview.setStyleSheet("margin-top:10px;border:0;")
        self.setPalette(palette)
        self.show()
        self.activateWindow()

    def addGlobalHotkey(self):
        self.hotKeys = Hotkey(self)
        self.hotKeys.sinOut.connect(self.change_visible)
        self.hotKeys.start()

    def change_visible(self):
        if self.isVisible():
            self.setVisible(False)
            self.clear_input_result()
        else:
            self.activateWindow()
            self.setVisible(True)

    def selectedUp(self):
        if self.result_model.selected:
            self.handleResultPeek(self.result_model.createIndex(self.result_model.selected - 1, 0))

    def selectedDown(self):
        if self.result_model.selected < self.result_model.rowCount() - 1:
            self.handleResultPeek(self.result_model.createIndex(self.result_model.selected + 1, 0))

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
                index.action.method()


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
            time.sleep(0.2)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WoxWidget()

    tuopan = QSystemTrayIcon(app)  # 创建托盘
    tuopan.setIcon(QIcon("images/app_search2.png"))  # 设置托盘图标
    tpMenu = QMenu()
    a1 = QAction(QIcon("images/app_search.png"), u'显示', app)  # 添加一级菜单动作选项(关于程序)
    a1.triggered.connect(ex.change_visible)
    a2 = QAction(QIcon("images/app_search.png"), u'退出', app)  # 添加一级菜单动作选项(退出程序)
    a2.triggered.connect(app.exit)
    tpMenu.addAction(a1)
    tpMenu.addAction(a2)
    tuopan.setContextMenu(tpMenu)  # 把tpMenu设定为托盘的右键菜单
    tuopan.show()  # 显示托盘

    sys.exit(app.exec_())
