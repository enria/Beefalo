import sys
import ctypes
import ctypes.wintypes
import win32con

from PyQt5.QtCore import QThread, pyqtSignal

from plugin_api import SettingInterface, PluginInfo

mod_keys = {"ctrl": win32con.MOD_CONTROL, "alt": win32con.MOD_ALT, "shift": win32con.MOD_SHIFT}


class Hotkey(QThread, SettingInterface):
    sinOut = pyqtSignal()
    inputSinOut = pyqtSignal([str])

    meta_info = PluginInfo()
    meta_info.path = ""

    def __init__(self, view):
        super(Hotkey, self).__init__(view)
        SettingInterface.__init__(self)
        self.view = view

    def run(self):
        user32 = ctypes.windll.user32
        param_map = {}
        try:
            param = 369
            key_map = self.get_setting("hotkeys")
            for key in key_map:
                to_query = key_map[key]
                keys = key.split("+")
                param += 1
                if not user32.RegisterHotKey(None, param, mod_keys[keys[0]], ord(keys[1])):
                    raise RuntimeError
                param_map[param] = to_query
        except BaseException as e:
            print(e)
            print("应用已启动：快捷键被占用")
            self.view.app.exit()
            sys.exit()
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    param = int(msg.wParam)
                    if param in param_map:
                        if not param_map[param]:
                            self.sinOut.emit()
                        else:
                            self.inputSinOut.emit(param_map[param])
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
