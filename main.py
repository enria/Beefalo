import inspect
import os
import sys
import uuid
import time
import ctypes
import re
import importlib
import win32con
from win32process import SuspendThread, ResumeThread

from PyQt5.QtCore import pyqtSignal, QThread, QObject, QEvent, Qt
from PyQt5.QtGui import QCursor, QKeySequence, QIcon
from PyQt5.QtWidgets import (QWidget, QApplication, QShortcut, QDesktopWidget, QLineEdit, QVBoxLayout, QListView,
                             QSizePolicy, QSystemTrayIcon, QMenu, QAction)

sys.path.append("plugin")
from plugin_api import AbstractPlugin, ContextApi, SettingInterface, PluginInfo
from result_list import ResultListModel, WidgetDelegate

from keyboard import Hotkey


class BeefaloWidget(QWidget, SettingInterface):
    meta_info = PluginInfo()
    meta_info.path = "."

    def __init__(self, root_app):
        super().__init__()
        self.app = root_app

        self.result_model = ResultListModel(self)
        self.result_model.sinOut.connect(self.adjust_size)
        self.ws_listview = QListView()
        self.ws_input = QLineEdit(self)  # 整型文本框
        self.delegate = WidgetDelegate()

        self.hotKeys = Hotkey(self.get_setting("hotkeys"))
        self.add_global_hotkey()

        self.plugins = {"*": []}
        self.plugin_types = []
        self.load_plugins()
        self.token = None

        self.installEventFilter(self)

        self.debounce_thread = DebounceThread(self)
        self.debounce_thread.sinOut.connect(self.async_change_result)
        self.debounce_thread.start()

        self.result_size = min(10, max(4, self.get_setting("result_size")))
        self.result_item_height = self.delegate.sizeHint(None, None).height()
        self.init_ui()

    def load_plugins(self):
        plugins_dir = "plugins"
        for plugin_dir in os.listdir(plugins_dir):
            if os.path.isdir(os.path.join(plugins_dir, plugin_dir)):
                sys.path.append(os.path.join(plugins_dir, plugin_dir))
                plugin_module = importlib.import_module("%s.%s" % (plugins_dir, plugin_dir))
                for att in dir(plugin_module):
                    try:
                        att_type = getattr(plugin_module, att)
                        if AbstractPlugin in inspect.getmro(att_type):
                            att_type.meta_info.path = os.path.join(plugins_dir, plugin_dir)
                            self.plugin_types.append(att_type)
                    except BaseException as e:
                        pass

        api = ContextApi(self.set_input_text, sys_tray.showMessage, self.change_theme, self.plugin_types, self,
                         self.get_theme)

        for plugin_type in self.plugin_types:
            plugin = plugin_type(api)
            if len(plugin.meta_info.keywords):
                for keyword in plugin.meta_info.keywords:
                    if self.plugins.get(keyword):
                        self.plugins[keyword].append(plugin)
                    else:
                        self.plugins[keyword] = [plugin]
            else:
                self.plugins["*"].append(plugin)

    def init_ui(self):
        self.setGeometry(0, 0, 800, 66 + self.result_item_height * (self.result_size + 2))
        self.setWindowTitle('Beefalo')

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setFixedHeight(66)

        vly = QVBoxLayout()

        font = self.ws_input.font()
        font.setFamily("微软雅黑")
        font.setPointSize(21)  # change it's size
        self.ws_input.setFont(font)
        self.ws_input.setFixedHeight(46)
        self.ws_input.setObjectName("MainLineEdit")
        self.ws_input.textChanged.connect(self.handle_text_changed)

        self.ws_input.returnPressed.connect(self.handle_result_selected)

        vly.addWidget(self.ws_input)

        self.setWindowFlag(Qt.ToolTip)

        self.ws_listview.setModel(self.result_model)
        self.ws_listview.setMaximumHeight(0)
        self.ws_listview.setItemDelegate(self.delegate)
        self.ws_listview.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.ws_listview.clicked.connect(self.handle_result_selected)
        self.ws_listview.setCursor(QCursor(Qt.PointingHandCursor))

        vly.addWidget(self.ws_listview)
        vly.setContentsMargins(8, 10, 8, 10)
        vly.setSpacing(0)
        self.setLayout(vly)
        self.ws_listview.setObjectName("ResultListView")
        self.setObjectName("MainWidget")
        self.show()
        self.activateWindow()

    def adjust_size(self):
        cnt = self.result_model.rowCount()
        height = self.result_item_height
        if cnt:
            self.ws_listview.setMaximumHeight(min(cnt, self.result_size) * height + 10)
            self.setFixedHeight(min(cnt, self.result_size) * height + 66 + 10)
        else:
            self.ws_listview.setMaximumHeight(min(cnt, self.result_size) * height)
            self.setFixedHeight(min(cnt, self.result_size) * height + 66)

    def change_theme(self, mainTheme, highlightItem):
        self.setStyleSheet(mainTheme)
        self.delegate.theme = highlightItem

    def get_theme(self):
        return self.delegate.theme

    def add_global_hotkey(self):
        self.hotKeys.sinOut.connect(self.change_visible)
        self.hotKeys.inputSinOut.connect(self.set_input_text)
        self.hotKeys.start()

        QShortcut(QKeySequence("Up"), self, self.selected_up)
        QShortcut(QKeySequence("Down"), self, self.selected_down)
        QShortcut(QKeySequence("PgUp"), self, self.selected_page_up)
        QShortcut(QKeySequence("PgDown"), self, self.selected_page_down)
        QShortcut(QKeySequence("Esc"), self, self.change_visible)

    def change_visible(self):
        if self.isVisible():
            self.setVisible(False)
            self.clear_input_result()
        else:
            self.activateWindow()
            self.ws_input.setFocus()
            self.setVisible(True)

    def set_input_text(self, text):
        self.ws_input.setText(text)
        self.activateWindow()
        self.setVisible(True)

    def selected_up(self):
        if self.result_model.rowCount() == 0:
            return
        self.handle_result_peek(
            self.result_model.createIndex((self.result_model.selected - 1) % self.result_model.rowCount(), 0))

    def selected_down(self):
        if self.result_model.rowCount() == 0:
            return
        self.handle_result_peek(
            self.result_model.createIndex((self.result_model.selected + 1) % self.result_model.rowCount(), 0))

    def selected_page_up(self):
        if self.result_model.rowCount() == 0:
            return
        self.handle_result_peek(
            self.result_model.createIndex(
                (self.result_model.selected - self.result_size) % self.result_model.rowCount(), 0))

    def selected_page_down(self):
        if self.result_model.rowCount() == 0:
            return
        self.handle_result_peek(
            self.result_model.createIndex(
                (self.result_model.selected + self.result_size) % self.result_model.rowCount(), 0))

    def clear_input_result(self):
        self.ws_input.setText("")

    def async_add_results(self, token, results):
        if token == self.token:
            self.result_model.addItems(results)

    def async_change_result(self, results):
        self.result_model.changeItems(results)
        self.handle_result_peek(self.result_model.createIndex(0, 0))

    def handle_text_changed(self):
        if self.debounce_thread.pause:
            self.debounce_thread.resume()
        self.debounce_thread.work = False

    def handle_result_peek(self, index):
        old = self.result_model.createIndex(self.result_model.selected, 0)
        self.result_model.selected = index.row()
        self.ws_listview.dataChanged(index, old)
        self.ws_listview.scrollTo(index)

    def handle_result_selected(self):
        if self.result_model.selected >= 0:
            index = self.result_model.data(self.result_model.createIndex(self.result_model.selected, 0))
            if index:
                if index.action.close:
                    self.change_visible()
                if index.action.method:
                    index.action.method(*index.action.args)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            self.change_visible()
            return True  # 说明这个事件已被处理，其他控件别插手
        if event.type() == QEvent.Close:
            print("hello?")
        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理


class DebounceThread(QThread):
    sinOut = pyqtSignal([list])

    def __init__(self, view: 'BeefaloWidget'):
        super(DebounceThread, self).__init__(view.thread())
        self.view = view
        self.work = False
        self.pause = True
        self.handle = None

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
                    pluginMath = re.match(r"(\w+)(\s*)(.*)", query)
                    matched_plugins = []
                    if pluginMath:
                        groups = pluginMath.groups()
                        if self.view.plugins.get(groups[0]):
                            keyword, text = groups[0], groups[2]
                            matched_plugins = [(plugin, keyword, text) for plugin in self.view.plugins.get(keyword)]

                    if not matched_plugins:
                        matched_plugins = [(plugin, "*", query) for plugin in self.view.plugins.get("*")]
                    elif not groups[1]:
                        matched_plugins += [(plugin, "*", query) for plugin in self.view.plugins.get("*")]

                    if matched_plugins:
                        for matched in matched_plugins:
                            plugin, keyword, text = matched
                            if plugin.meta_info.async_result:
                                item, asyncThread = plugin.query(keyword, text, self.view.token, self.obj)
                                result += item
                                if asyncThread:
                                    asyncThread.sinOut.connect(self.view.async_add_results)
                                    asyncThread.start()
                            else:
                                result += plugin.query(keyword, text)
                self.sinOut.emit(result)
                if self.work:
                    self.suspend()
            else:
                self.work = True

    def suspend(self):
        self.pause = True
        SuspendThread(self.handle)

    def resume(self):
        ResumeThread(self.handle)
        self.pause = False


global sys_tray

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys_tray = QSystemTrayIcon(app)
    window = BeefaloWidget(app)

    sys_tray.setIcon(QIcon("images/金牛.png"))  # 设置托盘图标
    sys_tray_menu = QMenu()
    show_action = QAction(u'显示', app)  # 添加一级菜单动作选项(关于程序)
    show_action.triggered.connect(window.change_visible)
    exit_action = QAction(u'退出', app)  # 添加一级菜单动作选项(退出程序)
    exit_action.triggered.connect(app.exit)
    sys_tray_menu.addAction(show_action)
    sys_tray_menu.addAction(exit_action)
    sys_tray.setContextMenu(sys_tray_menu)  # 把tpMenu设定为托盘的右键菜单
    sys_tray.show()  # 显示托盘

    sys.exit(app.exec_())
