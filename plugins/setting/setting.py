import inspect
import json
import os

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSize, QModelIndex, Qt
from PyQt5.QtGui import QIcon, QFont, QGuiApplication, QPixmap, QCursor
from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QDesktopWidget, QHBoxLayout, QListWidget, QListWidgetItem, \
    QWidget, QLabel, QGroupBox, QPushButton, QSpacerItem, QSizePolicy, QPlainTextEdit, QApplication
from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, get_logger
from result_model import ResultItem, ResultAction, MenuItem

log = get_logger("Setting")


class PluginEditorWidget(QWidget):
    def __init__(self, plugin: SettingInterface and AbstractPlugin, api: ContextApi):
        super(QWidget, self).__init__()
        self.plugin = plugin
        self.api = api
        self.vly = QVBoxLayout()
        self.setLayout(self.vly)
        self.label = QLabel(plugin.meta_info.name)
        font = QFont()
        font.setFamilies(["微软雅黑", "Segoe UI Symbol"])
        self.label.setFont(font)
        self.label.setObjectName("Title")

        self.editor = QPlainTextEdit()
        font = QFont()
        font.setFamilies(["Consolas"])
        self.editor.setFont(font)
        self.editor.setObjectName("Editor")

        button_group = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")
        button_group.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding))
        button_group.addWidget(self.save_btn)
        button_group.addWidget(self.reset_btn)
        font = QFont()
        font.setFamilies(["微软雅黑", "Segoe UI Symbol"])
        self.save_btn.setObjectName("SaveButton")
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_btn.setObjectName("ResetButton")
        self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))

        self.save_btn.setFont(font)
        self.reset_btn.setFont(font)
        self.vly.addWidget(self.label)
        self.vly.addWidget(self.editor)
        self.vly.addLayout(button_group)
        self.load_setting()
        self.save_btn.clicked.connect(self.save_setting)
        self.reset_btn.clicked.connect(self.load_setting)

    def load_setting(self):
        with open(self.plugin.setting_path, encoding="utf-8") as setting_file:
            self.editor.setPlainText(setting_file.read())

    def save_setting(self):
        try:
            json.loads(self.editor.toPlainText())
        except:
            return
        with open(self.plugin.setting_path, "w", encoding="utf-8") as setting_file:
            setting_file.write(self.editor.toPlainText())
        self.plugin.reload()

    def change_size(self):
        s = self.api.size_scale
        self.vly.setContentsMargins(10 * s.g, 10 * s.g, 0, 10 * s.g)

        font = self.label.font()
        font.setPixelSize(16 * s.f)
        self.label.setFont(font)
        self.label.setFixedHeight(48 * s.g)

        font = self.editor.font()
        font.setPixelSize(16 * s.f)
        self.editor.setFont(font)

        font = self.save_btn.font()
        font.setPixelSize(16 * s.f)
        self.save_btn.setFont(font)
        self.reset_btn.setFont(font)
        self.save_btn.setFixedHeight(30 * s.g)
        self.reset_btn.setFixedHeight(30 * s.g)


class PluginTitleWidget(QWidget):
    def __init__(self, plugin: AbstractPlugin, api: ContextApi):
        super(QWidget, self).__init__()
        self.plugin = plugin
        self.api = api
        hly = QHBoxLayout()
        hly.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        pm = QPixmap(os.path.join(plugin.meta_info.path, plugin.meta_info.icon))
        pm = pm.scaled(32, 32, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pm)

        self.name_label = QLabel(plugin.meta_info.name)
        font = QFont()
        font.setFamilies(["微软雅黑", "Segoe UI Symbol"])
        font.setPixelSize(16)
        self.name_label.setFont(font)
        self.name_label.setObjectName("Name")
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_label.setAlignment(Qt.AlignVCenter)

        hly.addWidget(self.icon_label)
        hly.addWidget(self.name_label)

        self.setLayout(hly)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def change_size(self):
        pm = QPixmap(os.path.join(self.plugin.meta_info.path, self.plugin.meta_info.icon))
        pm = pm.scaled(32 * self.api.size_scale.g, 32 * self.api.size_scale.g, Qt.IgnoreAspectRatio,
                       Qt.SmoothTransformation)
        self.icon_label.setPixmap(pm)
        font = self.name_label.font()
        font.setPixelSize(16 * self.api.size_scale.f)
        self.name_label.setFont(font)


class SettingDialog(QWidget):
    def __init__(self, plugin_info: PluginInfo, api: ContextApi):
        super().__init__()
        self.plugin_info = plugin_info
        self.api = api

        self.setWindowTitle("Setting")
        self.setWindowIcon(QIcon(os.path.join(self.plugin_info.path, "images/setting_icon.png")))
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.title_list = QListWidget()
        self.editor_list = QListWidget()
        self.inited = False
        self.title_list.setObjectName("TitleList")
        self.editor_list.setObjectName("EditorList")
        self.setObjectName("SettingPanel")

    def show(self) -> None:
        with open(os.path.join(self.plugin_info.path, "resource", "theme.css"), "r",
                  encoding="UTF-8") as theme_template:
            cur_theme = self.api.get_theme()
            self.setStyleSheet(theme_template.read().format(sb=cur_theme["color"],
                                                            tbc=cur_theme["background"],
                                                            thbc=cur_theme["result"]["highlight"]["background"],
                                                            tc=cur_theme["result"]["normal"]["color"],
                                                            thc=cur_theme["result"]["highlight"]["color"],
                                                            ebc=cur_theme["background"],
                                                            eibc=cur_theme["editor"]["background"],
                                                            eic=cur_theme["editor"]["color"],
                                                            eibd=cur_theme["editor"]["border"],
                                                            btbc=cur_theme["color"]))
        if not self.inited:
            self.init_widgets()

        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())

        self.setFixedWidth(800 * self.api.size_scale.g)
        self.setFixedHeight(600 * self.api.size_scale.g)
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry(screen).center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.title_list.setFixedWidth(150 * self.api.size_scale.g)
        for ii in range(self.title_list.count()):
            plugin_title_item = self.title_list.item(ii)
            plugin_title_item.setSizeHint(QSize(0, 48 * self.api.size_scale.g))
            self.title_list.itemWidget(plugin_title_item).change_size()

        for ii in range(self.editor_list.count()):
            plugin_editor_item = self.editor_list.item(ii)
            plugin_editor_item.setSizeHint(QSize(0, 600 * self.api.size_scale.g))
            self.editor_list.itemWidget(plugin_editor_item).change_size()

        super().show()

    def init_widgets(self):
        hly = QHBoxLayout()
        hly.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hly)
        hly.addWidget(self.title_list)
        hly.addWidget(self.editor_list)
        hly.setSpacing(0)

        for plugin in self.api.setting_plugins:
            plugin_title_item = QListWidgetItem()
            plugin_title_widget = PluginTitleWidget(plugin, self.api)
            self.title_list.addItem(plugin_title_item)
            self.title_list.setItemWidget(plugin_title_item, plugin_title_widget)

            plugin_editor_item = QListWidgetItem()
            plugin_editor_widget = PluginEditorWidget(plugin, self.api)
            self.editor_list.addItem(plugin_editor_item)
            self.editor_list.setItemWidget(plugin_editor_item, plugin_editor_widget)

        def selected_changed(item):
            self.editor_list.scrollToItem(self.editor_list.item(item.row()))

        self.title_list.clicked.connect(selected_changed)

        def prevent_wheel(event):
            return

        self.editor_list.wheelEvent = prevent_wheel
        self.editor_list.verticalScrollBar().hide()

        if self.api.setting_plugins:
            self.title_list.setCurrentRow(0)

        self.inited = True

    def choose_plugin(self, plugin_type):
        if not self.inited:
            self.init_widgets()
        index = 0
        for plugin in self.api.setting_plugins:
            if isinstance(plugin, plugin_type):
                self.title_list.setCurrentRow(index)
                self.editor_list.scrollToItem(self.editor_list.item(index))
                break
            index += 1
        self.show()


class SettingPlugin(AbstractPlugin):
    meta_info = PluginInfo("Setting", "Setting Beefalo and its plugins", "images/setting_icon.png",
                           ["setting"], False)

    def __init__(self, api: ContextApi):
        self.api = api
        self.panel = SettingDialog(self.meta_info, self.api)
        self.api.edit_setting = self.edit_setting

    def query(self, keyword, text, token=None, parent=None):
        return [ResultItem(self.meta_info, "Setting Beefalo",
                           "Setting Beefalo and its plugins",
                           "images/setting_icon.png",
                           ResultAction(self.panel.show, True))]

    def edit_setting(self, plugin_type):
        if AbstractPlugin in inspect.getmro(plugin_type) and \
                SettingInterface in inspect.getmro(plugin_type):
            self.panel.choose_plugin(plugin_type)
