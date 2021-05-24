import re
import os
import uuid
import time

from PyQt5.QtGui import QGuiApplication
from plugin_api import PluginInfo, ContextApi, AbstractPlugin, get_logger, I18nInterface
from result_model import ResultItem, ResultAction, MenuItem, CopyAction

log = get_logger("Typing")


class TypewriterPlugin(AbstractPlugin, I18nInterface):
    meta_info = PluginInfo(icon="images/keyboard.png", keywords=["typ"])

    def __init__(self, api: ContextApi):
        I18nInterface.__init__(self, api.language)
        self.api = api

        self.start_timer=None
        self.cur_doc_text=None

    def start_typing(self,doc):
        self.start_timer=time.time()

        with open(os.path.join(self.meta_info.path,"corpus",doc),encoding="utf-8") as doc_text:
            text=doc_text.read()
            text=text.replace("\n"," ")
            text=re.sub("\s+"," ",text)
            self.cur_doc_text=text
            
        
        text_item=ResultItem(self.meta_info, self.cur_doc_text, "0s", "images/sentence.png")

        self.api.change_results([text_item])
    
    def restart(self):
        self.start_timer=None
        self.cur_doc_text=None
        self.typed=None
    
    def typing(self,text:str):
        show_text=""
        if self.cur_doc_text.startswith(text):
            show_text_start=max(0,len(text)-20)
            show_text=self.cur_doc_text[show_text_start:]
            typed_time=time.time()-self.start_timer
            wpm=len(text)/(typed_time/60)
            text_item=ResultItem(self.meta_info, show_text, f" {typed_time:.1f}s    {len(text)}c    {wpm:.0f}WPM", "images/sentence.png")
        else:
            show_text_start=max(0,len(text)-10)
            show_text=self.cur_doc_text[show_text_start:]
            text_item=ResultItem(self.meta_info, "TYPO", show_text, "images/sentence.png")
        
        return text_item

    def doc_list(self):
        corpus=os.listdir(os.path.join(self.meta_info.path,"corpus"))
        results=[]
        for doc in corpus:
            icon = "images/document.png"
            action = ResultAction(self.start_typing, False, doc)
            item = ResultItem(self.meta_info, doc[:-4], doc, icon, action)
            results.append(item)

        return results


    def query(self, keyword, text, token=None, parent=None):
        if text and self.cur_doc_text:
            return [self.typing(text)]
        else:
            self.restart()
            results=self.doc_list()
            return results
