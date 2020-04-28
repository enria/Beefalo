from functools import lru_cache
import win32com.client


@lru_cache
def get_link_target(link_file):
    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(link_file)
    if scut.TargetPath:
        return scut.TargetPath
    return link_file


print(get_link_target(r"C:\Users\13972\Desktop\CodeBlocks.lnk"))
