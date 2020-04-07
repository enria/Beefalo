import os

from PyQt5.QtCore import QAbstractListModel, QModelIndex, QSize, QRect, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QBrush, QFont, QIcon
from PyQt5.QtWidgets import QStyledItemDelegate

from result_model import ResultItem


class ResultListModel(QAbstractListModel):
    sinOut = pyqtSignal()

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
            self.sinOut.emit()

    def addItems(self, itemDatas: list, change_size=True):
        if itemDatas:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(itemDatas) - 1)
            self.listItemData += itemDatas
            self.endInsertRows()
        self.selected = 0 if self.rowCount() > 0 else -1
        if change_size:
            self.sinOut.emit()

    def changeItems(self, itemDatas):
        change_size = len(itemDatas) != self.rowCount()
        self.clear()
        self.addItems(itemDatas, change_size)

    def deleteItem(self, index):
        del self.listItemData[index]
        self.sinOut.emit()

    def getItem(self, index):
        if -1 < index < len(self.listItemData):
            return self.listItemData[index]

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.listItemData) - 1)
        self.listItemData = []
        self.endRemoveRows()


DEFAULT_COLOR = {"color": "#000000", "background": "#4f6180", "highlight": "#000000"}


class WidgetDelegate(QStyledItemDelegate):

    def __init__(self, theme=DEFAULT_COLOR):
        super(WidgetDelegate, self).__init__()
        self.theme = theme

    def paint(self, painter, option, index):

        if index.data().selected:
            background_brush = QBrush(QColor(self.theme["background"]), Qt.SolidPattern)
            painter.fillRect(option.rect, background_brush)

        font = QFont('微软雅黑', 12)
        font.setWeight(60)
        sub_font = QFont('微软雅黑', 9)
        sub_font.setWeight(sub_font.weight() - 2)

        title = index.data().title
        sub_title = index.data().subTitle
        icon_size = QSize(32, 32)

        plugin_path = index.data().plugin_info.path
        if isinstance(index.data().icon, QIcon):
            icon = index.data().icon
        else:
            if index.data().root:
                pm = QPixmap(index.data().icon)
            else:
                pm = QPixmap(os.path.join(plugin_path, index.data().icon))
            pm = pm.scaled(32, 32, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pm)
        icon_rect = QRect(7, option.rect.top() + 7, 32, 32)
        header_rect = QRect(48, icon_rect.top() - 3, option.rect.width() - 48, 21)
        sub_title_rect = QRect(48, icon_rect.top() + 18, option.rect.width() - 48, 16)

        color = self.theme["color"]
        if index.data().selected:
            color = self.theme["highlight"]

        painter.drawPixmap(
            QPoint(icon_rect.left(), icon_rect.top()),
            icon.pixmap(icon_size.width(), icon_size.height()))
        painter.setFont(font)
        painter.setPen(QColor(color))
        painter.drawText(header_rect, Qt.AlignTop, title)

        painter.setFont(sub_font)
        painter.setPen(QColor(color))
        painter.drawText(sub_title_rect, Qt.AlignTop, sub_title)
        # painter.restore()

    def sizeHint(self, option, index: QModelIndex) -> QSize:
        return QSize(100, 46)
