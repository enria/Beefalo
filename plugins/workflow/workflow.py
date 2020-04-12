import os
import re
import subprocess
from enum import Enum, unique

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon, QFont, QGuiApplication
from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QDesktopWidget
from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, get_logger
from result_model import ResultItem, ResultAction, MenuItem

log = get_logger("Workflow")

@unique
class Source(Enum):
    Arg = "arg"
    Clipboard = "clipboard"
    Dialog = "dialog"
    Result = "result"


class Workflow(object):
    def __init__(self, name, script: str, source: Source, output: Source):
        self.name = name
        self.script = script
        self.source = source
        self.output = output


class Dialog(QDialog):
    def __init__(self, title, text, plugin_info: PluginInfo, api: ContextApi):
        super(QDialog, self).__init__(api.main_window)
        theme = api.get_theme()
        self.setWindowTitle("Beefalo Workflow: " + title)
        self.resize(600, 400)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        editor = QTextEdit(self)
        editor.setFont(QFont('Consolas', 12))
        editor.setText(text)
        editor.setStyleSheet('''
        QTextEdit{
            background-color: %s;
            color: %s;
            border: 1px solid rgba(0, 0, 0, 0.06);
            margin:0px;
        }''' % (theme["background"], theme["highlight"]))
        vly = QVBoxLayout()
        vly.addWidget(editor)
        vly.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vly)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(os.path.join(plugin_info.path, "images/workflow_script.png")))

    def closeEvent(self, event: QtGui.QCloseEvent):
        event.ignore()
        self.reject()


def run(flow: Workflow, args, plugin_info, api: ContextApi):
    output = ""

    if flow.script.endswith(".py"):
        try:
            process = subprocess.Popen(["python", flow.script] + args,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True, encoding="utf-8")
            process_out = process.stdout.read()
            process.stdout.close()
            process_error = process.stderr.read()
            process.stderr.close()
            if process_out and process_error:
                output = process_out + "\n" + process_error
            elif process_out:
                output = process_out
            elif process_error:
                output = process_error
        except BaseException as e:
            log.error(e)
            output = str(e)

    if flow.output == Source.Dialog:
        dialog = Dialog(flow.name, output, plugin_info, api)
        dialog.show()
    elif flow.output == Source.Clipboard:
        clipboard.setText(output)
    elif flow.output == Source.Result:
        result = ResultItem(plugin_info, flow.name, output, "images/workflow_script.png")
        result.menus = [MenuItem("复制", ResultAction(clipboard.setText, True, output))]
        api.change_results([result])


clipboard = QGuiApplication.clipboard()


class WorkflowPlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("Workflow", "执行脚本", "images/workflow_icon.png",
                           ["wf"], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.flows = []

        for info in self.get_setting("flows"):
            self.flows.append(Workflow(info["name"], info["script"], Source(info["input"]), Source(info["output"])))

    def query(self, keyword, text, token=None, parent=None):
        results = []
        script, args = "", []
        matched = re.match(r"(\w*?):(.*)", text)
        if matched:
            script, args = matched.groups()[0], [matched.groups()[1]]
        else:
            args = [text]
        for flow in self.flows:
            if script.lower() in flow.name.lower() or script.lower() in flow.script.lower():
                flow_arg = args
                if flow.source == Source.Clipboard:
                    flow_arg = [clipboard.text()]
                action = ResultAction(run, flow.output != Source.Result, flow, flow_arg, self.meta_info, self.api)
                results.append(ResultItem(self.meta_info, flow.name, flow.script, "images/workflow_script.png", action))
        return results
