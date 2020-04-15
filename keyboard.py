import sys
import ctypes
import ctypes.wintypes
import win32con

from PyQt5.QtCore import QThread, pyqtSignal

from plugin_api import SettingInterface, PluginInfo, get_logger

mod_keys = {"ctrl": win32con.MOD_CONTROL, "alt": win32con.MOD_ALT, "shift": win32con.MOD_SHIFT}
log = get_logger("热键")


class Hotkey(QThread, SettingInterface):
    sinOut = pyqtSignal()
    inputSinOut = pyqtSignal([str])

    meta_info = PluginInfo()
    meta_info.path = ""

    def __init__(self, key_map):
        super(Hotkey, self).__init__()
        self.key_map = key_map

    def run(self):
        user32 = ctypes.windll.user32
        param_map = {}
        try:
            param = 369
            for key in self.key_map:
                to_query = self.key_map[key]
                keys = key.split("+")
                param += 1
                if not user32.RegisterHotKey(None, param, mod_keys[keys[0]], ord(keys[1])):
                    log.error("快捷键 {} : 注册失败".format(key))
                    if not to_query:  # main hotkey
                        raise RuntimeError("主快捷无法注册，应用启动失败")
                param_map[param] = to_query
        except BaseException as e:
            log.error(e)
            sys.exit()
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    param = int(msg.wParam)
                    if param in param_map:
                        if not param_map[param]:  # main hotkey
                            self.sinOut.emit()
                        else:
                            self.inputSinOut.emit(param_map[param])
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
