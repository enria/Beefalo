import os
import re
import subprocess
import imp
from enum import Enum, unique

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon, QFont, QGuiApplication
from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QDesktopWidget
from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface, get_logger
from result_model import ResultItem, ResultAction, MenuItem, CopyAction

log = get_logger("Workspace")


class IDE(object):
    def __init__(self,plugin_info,name,keyword,script,icon):

        self.plugin_info=plugin_info

        self.name=name
        self.keyword=keyword
        self.script=script
        self.icon=icon

        self.instance=None
    
    def search(self,name):
        if self.instance==None:
            self.instance = imp.load_source(self.name, os.path.join(self.plugin_info.path,self.script))
        
        results=[]
        for title,sub_title,action in self.instance.search(name):
            item=ResultItem(self.plugin_info,title,sub_title,self.icon,ResultAction(action,True))
            results.append(item)

        return results





class WorkspacePlugin(AbstractPlugin, SettingInterface):
    meta_info = PluginInfo("Workspace", "打开工作空间", "images/workspace_icon.png",
                           [], False)

    def __init__(self, api: ContextApi):
        SettingInterface.__init__(self)
        self.api = api
        self.flows = []
        self.reload()

    def query(self, keyword, text):
        ide = self.ides[keyword]
        results=ide.search(text)
        return results

    def reload(self):
        SettingInterface.reload(self)
        self.load_ides()

    def load_ides(self):
        ides = self.get_setting("ides")
        keys = []
        self.ides = {}
        for info in ides:
            ide = IDE(self.meta_info,info["name"], info["keyword"], info["script"], info["icon"])
            self.ides[info["keyword"]] = ide
            keys.append(info["keyword"])
        self.meta_info.keywords = keys
