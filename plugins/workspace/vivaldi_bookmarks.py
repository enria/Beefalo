import os
import json
import re
import base64
from workspace import Workspace
from PyQt5.QtGui import QIcon, QPixmap

storage_path=os.path.join(os.path.expanduser('~'),"Library/Application Support/Vivaldi/Default/Bookmarks")

def multi_contain(total,parts):
    totle_low=total.lower()
    for p in parts:
        if p.lower() not in totle_low:
            return False
    return True

# 解决循环中的闭包问题
def wrapper(url):
    script_path = os.path.join(os.path.dirname(__file__),"resources","open_vivaldi_url.scpt")
    def open_url():
        os.system('osascript "%s" "%s"'%(script_path,url))
    return open_url

def get_url_icon(url):
    url_map_path = os.path.join(os.path.dirname(__file__),"resources","url_favicon.json")
    with open(url_map_path) as fin:
        url_map = json.load(fin)
    if url in url_map:
        return url_map[url]
    return None

def search(name):
    results=[]
    name=re.split("\s",name.strip())
    def find_bookmark(item,path):
        if item["type"]=="folder":
            newpath=f"{path}/{item['name']}"
            for c in item["children"]:
                find_bookmark(c,newpath)
        elif item["type"]=="url":
            title = item["name"]
            sub_title = f'{path}  {item["url"]}'
            if multi_contain(title+" "+sub_title,name):
                action=wrapper(item["url"])
                icon = get_url_icon(item["url"])
                results.append(Workspace(title, sub_title, action, icon))
    with open(storage_path,encoding="utf-8") as fjson:
        folders=json.load(fjson)["roots"]
        for folder in folders.values():
            find_bookmark(folder,"")
    return results
