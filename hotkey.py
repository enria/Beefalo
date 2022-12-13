import sys
import ctypes
import ctypes.wintypes

# import win32con

from PyQt5.QtCore import QThread, pyqtSignal
from pynput import keyboard 
from plugin_api import PluginInfo, get_logger

log = get_logger("热键")


class Hotkey(QThread):
    sin_out = pyqtSignal()
    input_sin_out = pyqtSignal([str])

    meta_info = PluginInfo()
    meta_info.path = ""

    def __init__(self, key_map):
        super(Hotkey, self).__init__()
        self.key_map = key_map

    def run(self):
        param_map = {}
        try:
            for key in self.key_map:
                to_query = self.key_map[key]
                if not to_query:  # main hotkey
                    param_map[key] = self.sin_out.emit
                else:
                    def change_text(to_query):
                        def func():
                            # print(to_query)
                            self.input_sin_out.emit(to_query)
                        return func

                    param_map[key] = change_text(to_query)
        except BaseException as e:
            log.error(e)
            sys.exit()
        try:
            with keyboard.GlobalHotKeys(param_map) as h:
                h.join()
        finally:
            pass
