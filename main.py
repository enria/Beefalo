import inspect
import os
import sys
import uuid
import time
import ctypes
import re
import importlib
import traceback

import requests
from PyQt5.QtMultimedia import QMediaPlayer
# from win32process import SuspendThread, ResumeThread

from PyQt5.QtCore import pyqtSignal, QThread, QObject, QEvent, QTimer, Qt
from PyQt5.QtGui import QCursor, QKeySequence, QIcon, QFontDatabase, QPalette
from PyQt5.QtWidgets import (QWidget, QApplication, QShortcut, QDesktopWidget, QLineEdit, QVBoxLayout, QListView,
                             QSizePolicy, QSystemTrayIcon, QMenu, QAction, QProgressBar,QMainWindow, QGraphicsBlurEffect)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.append("plugin")
from plugin_api import AbstractPlugin, ContextApi, SettingInterface, PluginInfo, get_logger

from hotkey import Hotkey
from result_list import ResultListModel, WidgetDelegate
from gui_size import WindowSize, ItemSize, SizeScale

# load plugin api from folder.
# For plugin development, just need to add the plugin api folder to path.

log = get_logger("主窗口")


class BeefaloWidget(QWidget, SettingInterface):
    meta_info = PluginInfo()
    meta_info.path = "."

    def __init__(self, root_app=None):
        super(BeefaloWidget, self).__init__(root_app)
        
        # super().__init__()
        self.setAttribute(Qt.WA_StyledBackground)
        self.app = root_app

        QFontDatabase.addApplicationFont("resources\fontawesome-regular.ttf")

        # define ui widgets
        self.result_model = ResultListModel(self)
        self.result_model.sin_out.connect(self.adjust_size)
        self.ws_listview = QListView()
        self.ws_progress_bar = QProgressBar()
        self.progress_cnt = 0
        self.ws_input = QLineEdit(self)  # 整型文本框
        self.ws_input.installEventFilter(self)
        self.ws_input_debounce_timer = QTimer(self)
        self.ws_input.textChanged.connect(self.handle_text_changed)
        self.obj = QObject()

        self.m_size = None
        self.delegate = WidgetDelegate(self.result_model, None)
        self.theme = {}
        self.instant = False

        self.hotKeys = Hotkey(self.get_setting("hotkeys"))
        self.add_global_hotkey()

        # load plugins
        self.api = None
        self.plugins = {"*": []}
        self.plugin_types = []
        self.setting_plugins = []
        self.load_plugins()
        self.token = None
        self.player = QMediaPlayer(self)  # 1

        self.installEventFilter(self)

        self.result_size = min(10, max(4, self.get_setting("result_size")))
        self.result_item_height = 0
        self.init_ui()

    def play_media(self, media_content):
        self.player.setMedia(media_content)
        self.player.play()

    def load_plugins(self):
        plugins_dir = self.get_setting("plugins_dir")
        for plugin_dir in sorted(os.listdir(plugins_dir)):
            if os.path.isdir(os.path.join(plugins_dir, plugin_dir)) and plugin_dir not in self.get_setting(
                    "exclude_plugin_dir"):
                # append plugin's folder path
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

        self.api = ContextApi(self.set_input_text, sys_tray.showMessage,
                              self.change_theme, self.plugin_types,
                              self.get_theme,
                              self.async_change_result, self.change_selected_result,
                              self.start_progress, self.end_progress,
                              self.play_media,
                              self.setting_plugins, self.get_setting("language"), None,self.winId())

        for plugin_type in self.plugin_types:
            plugin = plugin_type(self.api)
            if SettingInterface in inspect.getmro(plugin_type) and plugin.edit:
                self.setting_plugins.append(plugin)
            # log.info("插件初始化：{}".format(plugin.meta_info.name))
            if len(plugin.meta_info.keywords):
                for keyword in plugin.meta_info.keywords:
                    if self.plugins.get(keyword):
                        self.plugins[keyword].append(plugin)
                    else:
                        self.plugins[keyword] = [plugin]
            else:
                # add plugin to global
                self.plugins["*"].append(plugin)

    def init_ui(self):

        vly = QVBoxLayout()
        font = self.ws_input.font()
        font.setFamily("PingFang SC")
        # font.setPointSize(self.m_size.editor_font_size)  # change it's size
        self.ws_input.setFont(font)
        # self.ws_input.setFixedHeight(self.m_size.editor_height)
        self.ws_input.setObjectName("MainLineEdit")
        self.ws_input.textChanged.connect(self.handle_text_changed)
        self.ws_input.returnPressed.connect(self.handle_result_triggered)
        self.ws_input_debounce_timer.setSingleShot(True)

        self.ws_input_debounce_timer.timeout.connect(self.query)

        self.ws_progress_bar.setMaximum(0)
        self.ws_progress_bar.setMinimum(0)
        self.ws_progress_bar.setVisible(False)
        self.ws_progress_bar.setObjectName("QueryProgressBar")
        sp_retain = self.ws_progress_bar.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.ws_progress_bar.setSizePolicy(sp_retain)

        self.ws_listview.setObjectName("ResultListView")
        self.ws_listview.setModel(self.result_model)
        self.ws_listview.setItemDelegate(self.delegate)
        # self.ws_listview.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        self.ws_listview.clicked.connect(self.handle_result_triggered)
        self.ws_listview.setCursor(QCursor(Qt.PointingHandCursor))
        # self.ws_listview.installEventFilter(self)
        self.ws_listview.setMouseTracking(True)
        self.ws_listview.mouseMoveEvent = self.mouseMoveEvent

        vly.addWidget(self.ws_input)
        vly.addWidget(self.ws_progress_bar)
        vly.addWidget(self.ws_listview)
        vly.setSpacing(0)
        vly.setAlignment(Qt.AlignTop)
        self.setLayout(vly)
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("MainWidget")

    def start_progress(self):
        self.ws_progress_bar.setVisible(True)
        self.progress_cnt += 1

    def end_progress(self):
        self.progress_cnt -= 1
        if self.progress_cnt == 0:
            self.ws_progress_bar.setVisible(False)

    # def mouseMoveEvent(self, e):
    #     # todo mouse select result item
    #     # print(e.flags())
    #     pass

    def adjust_size(self):
        base_height = self.m_size.editor_height + self.m_size.main_padding[1] * 2
        max_height = base_height + self.m_size.result_margin_top + \
                     self.result_size * self.result_item_height
        height, cnt = base_height, self.result_model.rowCount()
        if cnt:
            height += self.m_size.result_margin_top
            height += (cnt - 1) * self.result_item_height
            if self.result_model.select.expand:  # add menu items height
                height += self.result_item_height \
                          + len(self.result_model.selected_item().menus) \
                          * self.delegate.i_size.menu_height
            else:
                height += self.result_item_height  # just an ordinary result item

        # TODO find more tricky method
        actual_height = min(height, max_height)
        if cnt:
            self.ws_listview.setFixedHeight(int(actual_height - base_height - self.m_size.result_margin_top))
        else:
            self.ws_listview.setFixedHeight(int(actual_height - base_height))
        self.ws_progress_bar.setFixedHeight(self.m_size.main_padding[1])
        self.setFixedHeight(int(actual_height))
        self.app.set_window_height(int(actual_height))

    def change_theme(self, css, theme):

        self.setStyleSheet(css)
        self.theme = theme
        self.delegate.theme = theme

    def get_theme(self):
        return self.theme

    def add_global_hotkey(self):
        self.hotKeys.sin_out.connect(self.change_visible)
        self.hotKeys.input_sin_out.connect(self.set_input_text)
        self.hotKeys.start()

        QShortcut(QKeySequence("Up"), self, self.selected_up)
        QShortcut(QKeySequence("Down"), self, self.selected_down)
        QShortcut(QKeySequence("PgUp"), self, self.selected_page_up)
        QShortcut(QKeySequence("PgDown"), self, self.selected_page_down)
        QShortcut(QKeySequence("Esc"), self, self.change_visible)

    def change_visible(self, keep=False):
        self.app.change_visible(keep)

    def change_screen(self, screen_rect):
        size_scale = SizeScale((screen_rect.width(), screen_rect.height()))
        self.api.size_scale = size_scale
        self.m_size = WindowSize(size_scale)
        self.delegate.i_size = ItemSize(size_scale)
        self.result_item_height = self.delegate.i_size.height
         
        self.setGeometry(0, 0, int(self.m_size.main_width),
                         int(self.m_size.editor_height + self.m_size.main_padding[1] * 2
                         + self.result_item_height * (self.result_size + 4)))

        # self.setFixedHeight(int(self.m_size.editor_height + self.m_size.main_padding[1] * 2
        #                     + self.result_item_height * (self.result_size + 2)))
        font = self.ws_input.font()
        # font.setPointSize(self.m_size.editor_font_size)  # change it's size
        font.setPixelSize(int(self.m_size.editor_font_size))
        self.ws_input.setFont(font)
        self.ws_input.setFixedHeight(int(self.m_size.editor_height))

        self.ws_progress_bar.setFixedHeight(int(self.m_size.main_padding[1]))

        self.layout().setContentsMargins(int(self.m_size.main_padding[0]),
                                         int(self.m_size.main_padding[1]),
                                         int(self.m_size.main_padding[0]),
                                         0)
        
        self.adjust_size()
        return self.m_size.main_width, int(self.m_size.editor_height + self.m_size.main_padding[1] * 2)

    def set_input_text(self, text):
        # in this case we should cancel the input debounce and don't change the selected row (try to)
        # the 'instant' variable make sense in self.async_change_result, debounce thread and delegate
        
        self.instant = True
        self.ws_input.setText(text)
        self.handle_text_changed()
        
        if not self.app.isVisible():
            self.change_visible()

    def clear_input_result(self):
        self.ws_input.setText("")

    def async_add_results(self, token, results):
        if token == self.token:
            self.result_model.addItems(results)

    def async_change_result(self, results,instant=False):
        self.result_model.changeItems(results, self.instant or instant)
        self.instant = False
        if self.result_model.select.row > -1:  # selected row may has been changed
            self.ws_listview.scrollTo(self.result_model.create_index())

    def change_selected_result(self, result):
        if self.result_model.select.valid():
            self.result_model.listItemData[self.result_model.select.row] = result
            self.result_model.select.selected_menu = -1
            self.repaint_selected_item()

    def selected_up(self):
        if self.result_model.rowCount() == 0:
            return
        if self.result_model.select.expand and self.result_model.select.selected_menu > -1:
            self.result_model.select.selected_menu -= 1
            self.repaint_selected_item()
        else:
            self.handle_result_selected(self.result_model.create_index(-1))

    def selected_down(self):
        if self.result_model.rowCount() == 0:
            return
        select = self.result_model.select
        if select.expand:
            if select.selected_menu < len(self.result_model.selected_item().menus) - 1:
                self.result_model.select.selected_menu += 1
            else:
                self.result_model.select.selected_menu = -1
            self.repaint_selected_item()
        else:
            self.handle_result_selected(self.result_model.create_index(1))

    def selected_page_up(self):
        if self.result_model.rowCount() == 0:
            return
        if self.result_model.create_index().row()\
            -self.result_size<0:
            self.handle_result_selected(self.result_model.createIndex(0, 0))
        else:
            self.handle_result_selected(self.result_model.create_index(-self.result_size))

    def selected_page_down(self):
        if self.result_model.rowCount() == 0:
            return
        # page down 不需要循环
        if self.result_model.create_index().row()\
            +self.result_size>=self.result_model.rowCount():
            self.handle_result_selected(self.result_model.createIndex(self.result_model.rowCount()-1, 0))
        else:
            self.handle_result_selected(self.result_model.create_index(self.result_size))

    def repaint_selected_item(self):
        # when change the selected row's style and display or hide it's menus
        cur = self.result_model.create_index()
        self.ws_listview.dataChanged(cur, cur)
        self.adjust_size()
        self.ws_listview.scrollTo(self.result_model.create_index())

    def handle_text_changed(self):
        if self.instant:
            self.ws_input_debounce_timer.start(0)
        else:
            self.ws_input_debounce_timer.start(50)

    def handle_result_selected(self, index):
        old = self.result_model.create_index()
        if self.result_model.select.expand:
            self.result_model.select.set_selected(index.row())
            self.adjust_size()
        else:
            self.result_model.select.set_selected(index.row())
        self.ws_listview.dataChanged(index, old)
        self.ws_listview.scrollTo(index)

    def handle_result_triggered(self, index=None):
        if index:
            self.handle_result_selected(index)
        if self.result_model.select.valid():
            index = self.result_model.data(self.result_model.create_index())
            if self.result_model.select.selected_menu == -1:
                action = index.action
            else:
                action = index.menus[self.result_model.select.selected_menu].action
            if action.close:
                self.change_visible()
            if action.method:
                action.method(*action.args)
    
    def query(self):
        result = []
        query = self.ws_input.text()
        self.token = str(uuid.uuid1())
        if len(query.strip()):
            pluginMath = re.match(r"([^\s]+)(\s*)(.*)", query)
            matched_plugins = []
            if pluginMath:
                groups = pluginMath.groups()
                if self.plugins.get(groups[0]):
                    keyword, text = groups[0], groups[2]
                    matched_plugins = [(plugin, keyword, text) for plugin in self.plugins.get(keyword)]
                if not groups[1]:  # there is not space, so add global plugins
                    matched_plugins += [(plugin, "*", query) for plugin in self.plugins.get("*")]

            if not matched_plugins:  # haven't matched any plugins, just treat it as global query
                matched_plugins = [(plugin, "*", query) for plugin in self.plugins.get("*")]

            for matched in matched_plugins:
                plugin, keyword, text = matched
                if plugin.meta_info.async_result:
                    item, asyncThread = plugin.query(keyword, text, self.token, self.obj)
                    result += item
                    if asyncThread:
                        asyncThread.sin_out.connect(self.async_add_results)
                        asyncThread.start()
                else:
                    result += plugin.query(keyword, text)
        
        self.async_change_result(result)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            self.change_visible(False)
            return True  # returning  True means not to pass to other widget's
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            if self.result_model.select.valid() and len(self.result_model.selected_item().menus):
                # change the selected row's vision
                if self.result_model.select.expand:
                    self.result_model.select.selected_menu = -1
                    self.result_model.select.expand = False
                else:
                    self.result_model.select.selected_menu = 0
                    self.result_model.select.expand = True
                self.repaint_selected_item()
            return True
        if obj == self.ws_listview:
            # print(event)
            pass
        return QObject.eventFilter(self, obj, event)  # 交由其他控件处理


global sys_tray

class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        
        self.screen_no = -1
        self.screen_width= 0

        self.press_x, self.press_y = 0,0

        # Widget
        self.widget = BeefaloWidget(self)
        self.widget_width = -1

        # Initial
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        if self.widget.get_setting("start_show"):
            self.change_visible()
        else:
            self.setVisible(False)
    
    def set_window_height(self, height):
        # self.resize(self.widget_width, height)
        self.setFixedHeight(height)
    
    def to_screen_center(self):
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        screen_rect = QApplication.desktop().screenGeometry(screen)
        if screen == self.screen_no and screen_rect.width==self.screen_width:
            return
        
        widget_width, widget_height = self.widget.change_screen(screen_rect)
        self.widget_width = widget_width
        self.setFixedHeight(widget_height)
        self.resize(widget_width, widget_height)
        
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry(screen).center()
        cp.setY(cp.y()*2//3)
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.screen_no = screen
        self.screen_width= screen_rect.width

    def change_visible(self, keep=False):
        if self.isVisible():
            self.setVisible(False)
            if not keep:
                self.widget.clear_input_result()
        else:
            self.to_screen_center()
            self.setVisible(True)
            self.activateWindow()
            self.raise_()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
    
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()
    
    def mouseReleaseEvent(self, QMouseEvent):
        self.moveFlag = False
        self.setCursor(Qt.ArrowCursor)

def start_app():
    # TODO i18n
    log.info("============================启动Beefalo============================")
    app = QApplication(sys.argv)
    global sys_tray
    sys_tray = QSystemTrayIcon(app)
    window = MainWindow(app)
    # window = BeefaloWidget(app)

    # I found the problem by trial and error.
    # It turned out the application closed only when mother is not shown.
    # The reason is that the default behavior is to quit the app when the last window close.
    # As the mother class is used as a daemon, this line must be added to change that behavior:
    app.setQuitOnLastWindowClosed(False)

    sys_tray.setIcon(QIcon("images/system_icon.png"))  # 设置托盘图标
    sys_tray_menu = QMenu()
    show_action = QAction(QIcon("images/radio-fill.ico"), u'显示', app)  # 添加一级菜单动作选项(关于程序)
    # show_action.triggered.connect(window.change_visible)
    exit_action = QAction(QIcon("images/exit.ico"), u'退出', app)  # 添加一级菜单动作选项(退出程序)
    exit_action.triggered.connect(app.exit)
    sys_tray_menu.addAction(show_action)
    sys_tray_menu.addAction(exit_action)
    sys_tray.setContextMenu(sys_tray_menu)  # 把tpMenu设定为托盘的右键菜单
    sys_tray.show()  # 显示托盘

    # window.show()
    # window.centralwidget.show()
    code = app.exec_()
    sys.exit(code)


if __name__ == '__main__':
    start_app()
