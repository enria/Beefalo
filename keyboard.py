import threading
import ctypes
import ctypes.wintypes
import win32con
from PyQt5.QtCore import QThread, pyqtSignal


class Hotkey(QThread):
    sinOut = pyqtSignal()
    inputSinOut = pyqtSignal([str])

    def __init__(self, view):
        super(Hotkey, self).__init__(view)

    def run(self):
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(None, 99, win32con.MOD_ALT, win32con.VK_SPACE):
            raise RuntimeError
        if not user32.RegisterHotKey(None, 100, win32con.MOD_ALT, 71):
            raise RuntimeError

        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == 99:
                        self.sinOut.emit()
                    if msg.wParam == 100:
                        self.inputSinOut.emit("g ")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
