import ctypes
import subprocess
from os import system

from plugin_api import AbstractPlugin, ContextApi, PluginInfo, SettingInterface
from result_model import ResultItem, ResultAction

user32 = ctypes.windll.user32


def lock():
    user32.LockWorkStation()


def sleep():
    subprocess.Popen("rundll32 powrprof.dll,SetSuspendState Hibernate")


def restart():
    system("shutdown -r -t 100")


class Command(object):
    def __init__(self, name, desc, method, icon):
        self.name = name
        self.desc = desc
        self.method = method
        self.icon = icon


class SystemCmdPlugin(AbstractPlugin):
    cmds = {
        "lock": Command("锁屏", "系统锁屏", lock, "images/system_cmd_lock.png"),
        "sleep": Command("睡眠", "系统睡眠", sleep, "images/system_cmd_sleep.png"),
        "restart": Command("重启", "系统重启", sleep, "images/system_cmd_restart.png")
    }

    meta_info = PluginInfo("系统命令", "系统/应用命令", "images/system_cmd_icon.png",
                           list(cmds.keys()), False)

    def __init__(self, api: ContextApi):
        self.api = api

    def query(self, keyword, text, token=None, parent=None):
        cmd = self.cmds[keyword]
        return [ResultItem(self.meta_info, cmd.name, cmd.desc, cmd.icon,
                           ResultAction(cmd.method, True))]
