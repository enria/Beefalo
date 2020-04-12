import os

from PyQt5.QtCore import QAbstractListModel, QModelIndex, QSize, QRect, QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QBrush, QFont, QIcon
from PyQt5.QtWidgets import QStyledItemDelegate

from result_model import ResultItem


class ItemSelection(object):
    def __init__(self):
        self.row = -1
        self.expand = False
        self.selected_menu = -1

    def valid(self):
        return self.row > -1

    def set_selected(self, row):
        self.row = row
        self.expand = False
        self.selected_menu = -1


class ResultListModel(QAbstractListModel):
    sinOut = pyqtSignal()

    def __init__(self, view):
        super().__init__()
        self.view = view
        self.listItemData = []
        self.select = ItemSelection()

    def create_index(self, inc=0):
        if self.rowCount():
            return self.createIndex((self.select.row + inc) % self.rowCount(), 0)
        return self.createIndex(0, 0)

    def selected_item(self):
        return self.data(self.create_index())

    def data(self, index, role=None):
        if -1 < index.row() < len(self.listItemData):
            return self.listItemData[index.row()]

    def rowCount(self, parent=QModelIndex()):
        return len(self.listItemData)

    def addItem(self, itemData: ResultItem):
        if itemData:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
            self.listItemData.append(itemData)
            self.endInsertRows()
            self.sinOut.emit()

    def addItems(self, itemDatas: list):
        if itemDatas:
            if not self.rowCount():
                self.select.set_selected(0)
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(itemDatas) - 1)
            self.listItemData += itemDatas
            self.endInsertRows()
            self.sinOut.emit()

    def changeItems(self, itemDatas):
        change_size = len(itemDatas) != self.rowCount() or self.select.expand
        self.clear()
        if itemDatas:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(itemDatas) - 1)
            self.listItemData = itemDatas
            self.endInsertRows()
            self.select.set_selected(0)
        else:
            self.select.set_selected(-1)
        if change_size:
            self.sinOut.emit()

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

    def __init__(self, model: ResultListModel, theme=DEFAULT_COLOR):
        super(WidgetDelegate, self).__init__()
        self.theme = theme
        self.model = model

    def paint(self, painter, option, index):

        if index.row() == self.model.select.row and self.model.select.selected_menu == -1:
            background_brush = QBrush(QColor(self.theme["background"]), Qt.SolidPattern)
            painter.fillRect(QRect(0, option.rect.top(), option.rect.width(), 48), background_brush)
            if len(index.data().menus) and not self.model.select.expand:
                pm = QPixmap("images/expand_menu.png")
                pm = pm.scaled(24, 24, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(QPoint(option.rect.width() - 32, option.rect.top() + 12), pm)

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
        header_rect = QRect(48, icon_rect.top() - 3, option.rect.width() - 96, 21)
        sub_title_rect = QRect(48, icon_rect.top() + 18, option.rect.width() - 96, 16)

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

        if self.model.select.expand and self.model.select.row == index.row():
            for i in range(len(index.data().menus)):
                menu_rect = QRect(48, option.rect.top() + 48 + i * 23, option.rect.width() - 48, 23)
                if i == self.model.select.selected_menu:
                    background_brush = QBrush(QColor(self.theme["background"]), Qt.SolidPattern)
                    painter.fillRect(menu_rect, background_brush)
                painter.setFont(sub_font)
                painter.setPen(QColor(color))
                painter.drawText(QRect(menu_rect.left() + 7, menu_rect.top(), menu_rect.width(), menu_rect.height()),
                                 Qt.AlignVCenter, index.data().menus[i].title)
        # painter.restore()

    def sizeHint(self, option, index: QModelIndex) -> QSize:
        height = 46
        if index and index.row() == self.model.select.row and self.model.select.expand:
            height += 23 * len(index.data().menus)
        return QSize(100, height)
