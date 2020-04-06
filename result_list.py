import os
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QRect, QPoint
from PyQt5.QtGui import QPixmap, QColor, QBrush, QFont, QIcon
from PyQt5.QtWidgets import QStyledItemDelegate
from result_model import ResultItem


class ResultListModel(QAbstractListModel):
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
            self.view.ws_listview.setMaximumHeight(min(cnt, 6) * 46 + 10)
            self.view.setFixedHeight(min(cnt, 6) * 46 + 66 + 10)
        else:
            self.view.ws_listview.setMaximumHeight(min(cnt, 6) * 46)
            self.view.setFixedHeight(min(cnt, 6) * 46 + 66)


DEFAULT_COLOR = {"color": "#000000", "background": "#4f6180", "highlight": "#000000"}


class WidgetDelegate(QStyledItemDelegate):
    def __init__(self, theme=DEFAULT_COLOR):
        super(WidgetDelegate, self).__init__()
        self.theme = theme

    def paint(self, painter, option, index):


        if index.data().selected:
            background_brush = QBrush(QColor(self.theme["background"]), QtCore.Qt.SolidPattern)
            painter.fillRect(option.rect, background_brush)

        font = QFont('微软雅黑', 12)
        font.setWeight(60)
        SubFont = QFont('微软雅黑', 9)
        SubFont.setWeight(SubFont.weight() - 2)

        headerText = index.data().title
        subText = index.data().subTitle
        iconsize = QSize(32, 32)

        plugin_path = index.data().plugin_info.path
        if isinstance(index.data().icon, QIcon):
            icon = index.data().icon
        else:
            if index.data().root:
                pm = QPixmap(index.data().icon)
            else:
                pm = QPixmap(os.path.join(plugin_path, index.data().icon))
            pm = pm.scaled(32, 32, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
            icon = QIcon(pm)
        iconRect = QRect(7, option.rect.top() + 7, 32, 32)
        headerRect = QRect(48, iconRect.top() - 3, option.rect.width() - 48, 21)
        subheaderRect = QRect(48, iconRect.top() + 18, option.rect.width() - 48, 16)

        color = self.theme["color"]
        if index.data().selected:
            color = self.theme["highlight"]

        painter.drawPixmap(
            QPoint(iconRect.left(), iconRect.top()),
            icon.pixmap(iconsize.width(), iconsize.height()))
        painter.setFont(font)
        painter.setPen(QColor(color))
        painter.drawText(headerRect, QtCore.Qt.AlignTop, headerText)

        painter.setFont(SubFont)
        painter.setPen(QColor(color))
        painter.drawText(subheaderRect, QtCore.Qt.AlignTop, subText)
        # painter.restore()

    def sizeHint(self, option, index: QtCore.QModelIndex) -> QSize:
        return QSize(100, 46)
