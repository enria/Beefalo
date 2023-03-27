import os
import json
import re
from urllib.parse import unquote
import sqlite3
import urllib.parse
from subprocess import Popen

from workspace import Workspace

vsc_path="code"

last_update=None
storage_path=os.path.join(os.path.expanduser('~'),"Library/Application Support/Code/User/globalStorage/state.vscdb")
entries=[]


def multi_contain(total,parts):
    totle_low=total.lower()
    for p in parts:
        if p.lower() not in totle_low:
            return False
    return True

# 解决循环中的闭包问题
def wrapper(uri):
    def open_workspace():
        Popen(["/usr/local/bin/code","--folder-uri","%s"%uri])
    return open_workspace

def delete_worksapce_item(item):
    def _delete():
        conn = sqlite3.connect(f'file://{storage_path}', uri=True)
        origin_entries=next(conn.execute(""" select value from ItemTable where key="history.recentlyOpenedPathsList" """))[0]
        origin_entries = json.loads(origin_entries)
        entries=origin_entries["entries"]
        entries = list(filter(lambda entry: entry!=item, entries))
        origin_entries["entries"] = entries
        cur = conn.cursor()
        cur.execute('update ItemTable set value = ? where key="history.recentlyOpenedPathsList"',(json.dumps(origin_entries),))
        conn.commit()
        conn.close()
    return _delete

def search(name):
    results=[]
    name=re.split("\s",name.strip())
    global entries,last_update
    if last_update!=os.path.getmtime(storage_path): # update db cache
        conn = sqlite3.connect(f'file://{storage_path}?mode=ro', uri=True)
        entries=next(conn.execute(""" select value from ItemTable where key="history.recentlyOpenedPathsList" """))[0]
        entries=json.loads(entries)["entries"]
        conn.close()
        last_update=os.path.getmtime(storage_path)
    
    for entry in entries:
        if "folderUri" in entry:
            folder_uri=entry["folderUri"]
            

            label=entry.get("label",folder_uri.split("//")[-1])
            title=label
            sub_title=label

            if folder_uri.startswith("vscode-remote:"):
                title = re.split("/|(\\\\)",folder_uri)[-1]
            elif folder_uri.startswith("file:///"):
                title = re.split("/|(\\\\)",folder_uri)[-1]
            
            if not title:
                title="/"
            title = urllib.parse.unquote(title)
            sub_title = urllib.parse.unquote(sub_title)

            if not multi_contain(sub_title,name):
                continue

            action=wrapper(folder_uri)
            menus = [delete_worksapce_item(entry)]
            results.append(Workspace(title, sub_title, action, menus=menus))

    return results
