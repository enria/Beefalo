from random import random

from PyQt5.QtCore import QAbstractListModel, QModelIndex


class ContextApi:
    def __init__(self, change_query, show_message, change_theme, get_setting, set_setting):
        self.change_query = change_query
        self.show_message = show_message
        self.change_theme = change_theme
        self.get_setting = get_setting
        self.set_setting = set_setting


class ResultAction:
    def __init__(self, method, close=True, *args):
        self.method = method
        self.close = close
        self.args = args


class ResultItem:
    def __init__(self, title=None, subTitle=None, icon=None, action=ResultAction(None, True)):
        self.icon = icon
        self.title = title
        self.subTitle = subTitle
        self.action = action
        self.selected = False


class ResultListMode(QAbstractListModel):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.listItemData = []
        self.selected = -1

    def data(self, index, role=None):
        if -1 < index.row() < len(self.listItemData):
            self.listItemData[index.row()].selected = (index.row() == self.selected)
            return self.listItemData[index.row()]

    def rowCount(self, parent=QModelIndex()):
        return len(self.listItemData)

    def addItem(self, itemData: ResultItem):
        if itemData:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self.listItemData.append(itemData)
            self.endInsertRows()
            self.adjustSize()

    def addItems(self, itemDatas: list):
        if itemDatas:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(itemDatas) - 1)
            self.listItemData += itemDatas
            self.endInsertRows()
            self.selected = 0 if self.rowCount() > 0 else -1
        self.adjustSize()

    def changeItems(self, itemDatas):
        self.clear()
        self.addItems(itemDatas)

    def deleteItem(self, index):
        del self.listItemData[index]
        self.adjustSize()

    def getItem(self, index):
        if -1 < index < len(self.listItemData):
            return self.listItemData[index]

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.listItemData) - 1)
        self.listItemData = []
        self.endRemoveRows()
        self.adjustSize()

    def adjustSize(self):
        cnt = self.rowCount()
        if cnt:
            self.view.listview.setMaximumHeight(min(cnt, 6) * 46 + 10)
            self.view.setFixedHeight(min(cnt, 6) * 46 + 66 + 10)
        else:
            self.view.listview.setMaximumHeight(min(cnt, 6) * 46)
            self.view.setFixedHeight(min(cnt, 6) * 46 + 66)
