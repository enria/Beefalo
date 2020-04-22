import os
import re
import subprocess
from enum import Enum, unique
import qrcode

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QGuiApplication, QPixmap
from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QDesktopWidget, QLabel
from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, get_logger
from result_model import ResultItem, ResultAction, MenuItem

log = get_logger("Qr Code")


class Dialog(QDialog):
    def __init__(self, text, plugin_info: PluginInfo, api: ContextApi):
        super(QDialog, self).__init__(api.main_window)
        theme = api.get_theme()
        self.setWindowTitle("QR Code ")
        self.resize(300, 300)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        vly = QVBoxLayout()
        try:
            w_code_img = QLabel(self)
            qr = qrcode.QRCode(
                version=4,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=2,
            )
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image()
            img.save(os.path.join(plugin_info.path, "temp.png"))
            img = QPixmap(os.path.join(plugin_info.path, "temp.png"))
            img = img.scaled(300, 300, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            w_code_img.setPixmap(img)
            vly.addWidget(w_code_img)
        except BaseException as e:
            w_code_text = QLabel(self)
            w_code_text.setText("The text is too long!")
            w_code_text.setFont(QFont('微软雅黑', 12))
            vly.addWidget(w_code_text)

        vly.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vly)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(os.path.join(plugin_info.path, "images/qrcode_icon.png")))


clipboard = QGuiApplication.clipboard()


class QrCodePlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("QR Code", "Generate Qr Code by what you are typing", "images/qrcode_icon.png",
                           ["qrc"], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api

    def show_qrcode(self, text):
        dialog = Dialog(text, self.meta_info, self.api)
        dialog.show()

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if not text:
            text = QGuiApplication.clipboard().text()
        results.append(ResultItem(self.meta_info,
                                  "Generate QR code image", text, "images/qrcode_icon.png",
                                  ResultAction(self.show_qrcode, True, text)))
        return results
