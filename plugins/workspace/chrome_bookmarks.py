import os
import json
import re
import webbrowser
from urllib.parse import unquote

storage_path=os.path.join(os.path.expanduser('~'),"AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks")

def multi_contain(total,parts):
    totle_low=total.lower()
    for p in parts:
        if p.lower() not in totle_low:
            return False
    return True

# 解决循环中的闭包问题
def wrapper(url):
    def open_url():
        webbrowser.open(url)
    return open_url

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
                results.append((title,sub_title,action))
    with open(storage_path,encoding="utf-8") as fjson:
        folders=json.load(fjson)["roots"]
        for folder in folders.values():
            find_bookmark(folder,"")
    return results
