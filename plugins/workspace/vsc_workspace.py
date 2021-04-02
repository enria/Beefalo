import os
import json
import re
from urllib.parse import unquote

vsc_path="code"
storage_path=os.path.join(os.path.expanduser('~'),"AppData/Roaming/Code","storage.json")

def multi_contain(total,parts):
    totle_low=total.lower()
    for p in parts:
        if p.lower() not in totle_low:
            return False
    return True

# 解决循环中的闭包问题
def wrapper(uri):
    def open_workspace():
        os.system('code --folder-uri "%s"'%uri)
    return open_workspace

def search(name):
    results=[]
    name=re.split("\s",name.strip())
    with open(storage_path) as fjson:
        entries=json.load(fjson)["openedPathsList"]["entries"]
        for entry in entries:
            if "folderUri" in entry:
                folder_uri=entry["folderUri"]
                if "label" in entry:
                    sub_title = unquote(entry["label"])
                    title = re.split("/|(\\\\)",sub_title)[-1]
                else:
                    sub_title = re.sub("^.*://","",unquote(folder_uri))
                    title = re.split("/|(\\\\)",sub_title)[-1]
                
                if not multi_contain(sub_title,name):
                    continue
                
                action=wrapper(folder_uri)
                results.append((title,sub_title,action))
    return results
