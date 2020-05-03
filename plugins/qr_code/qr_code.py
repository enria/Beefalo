import os
import qrcode
import re
import hashlib
from urllib.parse import quote, unquote

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QGuiApplication, QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDesktopWidget, QLabel
from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, get_logger
from result_model import ResultItem, ResultAction

log = get_logger("Qr Code")


class Dialog(QDialog):
    def __init__(self, text, plugin_info: PluginInfo, api: ContextApi):
        super(QDialog, self).__init__()
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
            log.error(e)
            w_code_text = QLabel(self)
            w_code_text.setText("The text is too long!")
            w_code_text.setFont(QFont('微软雅黑', 12))
            vly.addWidget(w_code_text)

        vly.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vly)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(os.path.join(plugin_info.path, "images/qrcode_icon.png")))


class QrCodePlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("QR Code", "Generate Qr Code by what you are typing", "images/qrcode_icon.png",
                           ["qrc"], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.server = None
        self.dialog: Dialog = None
        self.build_server()

    def show_qrcode(self, text):
        self.dialog = Dialog(text, self.meta_info, self.api)
        self.dialog.show()

    def copy_uploaded_text(self):
        QGuiApplication.clipboard().setText(self.server.uploaded_text)
        self.server.uploaded_text = ""

    def query(self, keyword, text, token=None, parent=None):
        results = []
        if not text:
            text = QGuiApplication.clipboard().text()
            if self.server.uploaded_text:
                copy_item = ResultItem(self.meta_info,
                                       "Copy the uploaded text",
                                       self.server.uploaded_text,
                                       "images/qrcode_copy.png",
                                       ResultAction(self.copy_uploaded_text, True))
                results.append(copy_item)
        url = self.server.set_text(text)
        results.append(ResultItem(self.meta_info,
                                  "Generate QR Code", text, "images/qrcode_icon.png",
                                  ResultAction(self.show_qrcode, True, url)))
        return results

    def build_server(self):
        self.server = WebServer(self)
        self.server.query_sin_out.connect(self.api.change_query)
        self.server.start()

    def reload(self):
        SettingInterface.reload(self)
        if self.server:
            self.server.terminate()
            self.build_server()


class WebServer(QThread):
    query_sin_out = pyqtSignal([str])

    def __init__(self, plugin: QrCodePlugin):
        super(WebServer, self).__init__()
        self.plugin = plugin
        self.web_file = "README.md"
        self.web_text = "None"
        self.server_host = self.plugin.get_setting("server")["host"]
        self.server_port = self.plugin.get_setting("server")["port"]
        self.uploaded_text = ""
        self.app = None

    def run(self):
        from flask import Flask, send_file, render_template, make_response, request, redirect
        self.app = Flask(__name__,
                         static_url_path='/assets',
                         static_folder='templates/assets')

        @self.app.route('/file')
        def download_file():
            if self.web_file:
                file_name = os.path.basename(self.web_file)
                response = make_response(send_file(self.web_file, as_attachment=True))
                response.headers["Content-Disposition"] = "attachment; filename={}".format(
                    file_name.encode().decode('latin-1'))
                return response
            else:
                return "File not found"

        @self.app.route('/text', methods=['GET', 'POST'])
        def print_text():
            if request.method == 'GET':
                return render_template('text.html', text=self.web_text)
            if request.method == "POST":
                data = request.form
                if data.get("text"):
                    self.uploaded_text = data.get("text")
                    self.query_sin_out.emit("{} ".format(self.plugin.meta_info.keywords[0]))
            return {"status": 200, "msg": "success"}

        @self.app.route("/", methods=["GET"])
        def home():
            to = request.args.get("to")
            if not to:
                return "Hello Beefalo QR Code plugin"
            to = unquote(to, 'utf-8')
            arg = request.args.get("arg")
            if self.plugin.dialog and self.plugin.dialog.isVisible():
                self.plugin.dialog.close()
            if arg:
                to += unquote(arg, 'utf-8')
            return redirect(to)

        try:
            self.app.run(port=self.server_port, host=self.server_host)
        except:
            log.error("Qr code server starting failed")

    def set_text(self, text: str):
        arg = ""
        if re.match(r"^https?://.+", text):
            to = text
        else:
            route = ""
            if text.startswith("file:///"):
                file_path = re.sub("^file:///", "", text)
                if os.path.isfile(file_path):
                    md5 = hashlib.md5()
                    md5.update(file_path.encode("utf-8"))
                    self.web_file = file_path
                    arg = "?hash=" + md5.hexdigest()
                    route = "file"
            if not route:
                self.web_text = text
                route = "text"
            to = route
        return "http://{}:{}?to={}&arg={}".format(self.server_host, self.server_port, quote(to), quote(arg, "utf-8"))
