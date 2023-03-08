import os

from PyQt5.QtCore import QAbstractListModel, QModelIndex, QSize, QRect, QPoint, Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QColor, QBrush, QFont, QIcon, QPainterPath, QPen, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QStyledItemDelegate, QAbstractItemDelegate,QToolTip

from result_model import ResultItem

from gui_size import ItemSize
import re


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
    sin_out = pyqtSignal()

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
            self.sin_out.emit()

    def addItems(self, itemDatas: list):
        if itemDatas:
            if not self.rowCount():
                self.select.set_selected(0)
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(itemDatas) - 1)
            self.listItemData += itemDatas
            self.endInsertRows()
            self.sin_out.emit()

    def changeItems(self, itemDatas, instant):
        change_size = len(itemDatas) != self.rowCount() or self.select.expand
        self.clear()
        if itemDatas:
            self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(itemDatas) - 1)
            self.listItemData = itemDatas
            if instant:
                if self.select.row == -1:
                    self.select.set_selected(0)
                elif self.select.row >= self.rowCount():
                    self.select.set_selected(self.rowCount() - 1)
                else:
                    self.select.set_selected(self.select.row)
            else:
                self.select.set_selected(0)
            self.endInsertRows()
        else:
            self.select.set_selected(-1)
        if change_size:
            self.sin_out.emit()

    def deleteItem(self, index):
        del self.listItemData[index]
        self.sin_out.emit()

    def getItem(self, index):
        if -1 < index < len(self.listItemData):
            return self.listItemData[index]

    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.listItemData) - 1)
        self.listItemData = []
        self.endRemoveRows()


DEFAULT_COLOR = {
    "color": "#ac6218",
    "result": {
        "background": "#1e1f1c",
        "normal": {
            "color": "#b6b7b5"
        },
        "highlight": {
            "background": "#414339",
            "color": "#b6b7b5"
        },
        "scroll": "#414339"
    }
}

def rgba2qcolor(rgba:str):
    rgba=rgba.replace(" ","")
    rgba=list(re.match("rgba\((.+),(.+),(.+),(.+)\)",rgba).groups())
    if rgba[-1].endswith("%"):
        rgba[-1]=int(rgba[-1][:-1])/100*255
    rgba=list(map(int, rgba))
    return QColor(rgba[0],rgba[1],rgba[2],rgba[3])
    
    


class WidgetDelegate(QAbstractItemDelegate):

    def __init__(self, model: ResultListModel, i_size: ItemSize, theme=DEFAULT_COLOR):
        super(WidgetDelegate, self).__init__()
        self.theme = theme
        self.model = model
        self.i_size = i_size
        self.menu_icon = {}

    def get_menu_icon_data(self, color):
        if color in self.menu_icon:
            return self.menu_icon[color]
        with open("images/down.svg", "r", encoding="UTF-8") as svg:
            svg_str = svg.read()
            svg_str = svg_str.replace('#ffffff', color)
            svg_data = svg_str.encode("utf-8")
            render = QSvgRenderer(svg_data)
            self.menu_icon[color] = render
            return render

    def paint(self, painter, option, index):
        theme = self.theme["result"]
        highlight_background=QColor(theme["highlight"]["background"]) \
            if theme["highlight"]["background"].startswith("#") \
            else rgba2qcolor(theme["highlight"]["background"])
        if index.row() == self.model.select.row and self.model.select.selected_menu == -1:
            if theme["highlight"].get("border_radius", 0):
                radius = theme["highlight"].get("border_radius", 0)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addRoundedRect(0, option.rect.top(), option.rect.width(), self.i_size.height, radius, radius)
                pen = QPen(Qt.green, 10)
                painter.setPen(pen)
                painter.fillPath(path, highlight_background)
            else:
                background_brush = QBrush(highlight_background, Qt.SolidPattern)
                painter.fillRect(QRect(0, option.rect.top(), option.rect.width(), self.i_size.height), background_brush)
            if len(index.data().menus) and not self.model.select.expand:
                render = self.get_menu_icon_data(self.theme["color"])
                left = option.rect.width() - (self.i_size.drop_size[0] + self.i_size.drop_margin[0])
                top = option.rect.top() + self.i_size.drop_margin[1]
                render.render(painter, QRectF(left, top, self.i_size.drop_size[0], self.i_size.drop_size[1]))

        font = QFont()
        font.setFamilies(["PingFang SC", "FontAwesome"])
        font.setPixelSize(self.i_size.font_size)
        font.setWeight(self.i_size.font_weight)
        sub_font = QFont()
        sub_font.setFamilies(font.families())
        sub_font.setPixelSize(self.i_size.sub_font_size)

        title = index.data().title
        sub_title = index.data().subTitle
        icon_size = QSize(self.i_size.icon_size[0], self.i_size.icon_size[1])

        plugin_path = index.data().plugin_info.path
        dr = self.i_size.device_ratio
        if isinstance(index.data().icon, QIcon):
            pm = index.data().icon.pixmap(QSize(icon_size.width()*dr, icon_size.height()*dr))
            icon = QIcon(pm)
        else:
            if index.data().root:
                pm = QPixmap(index.data().icon)
            else:
                pm = QPixmap(os.path.join(plugin_path, index.data().icon))
            pm = pm.scaled(icon_size.width()*dr, icon_size.height()*dr, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)            
            icon = QIcon(pm)
        icon_rect = QRect(self.i_size.icon_margin[0], option.rect.top() + self.i_size.icon_margin[1], icon_size.width(),
                          icon_size.height())
        header_rect = QRect(self.i_size.title_margin[0], option.rect.top() + self.i_size.title_margin[1],
                            option.rect.width() - self.i_size.height * 2,
                            self.i_size.title_height)
        sub_title_rect = QRect(self.i_size.height, header_rect.bottom(), header_rect.width(),
                               self.i_size.sub_title_height)

        color = theme["normal"]["color"]
        if index.row() == self.model.select.row and self.model.select.selected_menu == -1:
            color = theme["highlight"]["color"]
        
        pm=icon.pixmap(icon_size.width()*dr, icon_size.height()*dr)
        pm.setDevicePixelRatio(dr)
        painter.drawPixmap(QPoint(icon_rect.left(), icon_rect.top()),pm)
        painter.setFont(font)
        painter.setPen(QColor(color))
        painter.drawText(header_rect, Qt.AlignTop, title)

        painter.setFont(sub_font)
        painter.setPen(QColor(color))
        painter.drawText(sub_title_rect, Qt.AlignTop, sub_title)

        if self.model.select.expand and self.model.select.row == index.row():
            for i in range(len(index.data().menus)):
                color = theme["normal"]["color"]
                menu_rect = QRect(self.i_size.height,
                                  option.rect.top() + self.i_size.height + i * self.i_size.menu_height,
                                  option.rect.width() - self.i_size.height, self.i_size.menu_height)
                if i == self.model.select.selected_menu:
                    background_brush = QBrush(highlight_background, Qt.SolidPattern)
                    painter.fillRect(menu_rect, background_brush)
                    color = theme["highlight"]["color"]
                painter.setFont(sub_font)
                painter.setPen(QColor(color))
                painter.drawText(
                    QRect(menu_rect.left() + self.i_size.menu_left_margin, menu_rect.top(), menu_rect.width(),
                          menu_rect.height()),
                    Qt.AlignVCenter, index.data().menus[i].title)
        # painter.restore()

    def sizeHint(self, option, index: QModelIndex) -> QSize:
        height = self.i_size.height
        if index and index.row() == self.model.select.row and self.model.select.expand:
            height += self.i_size.menu_height * len(index.data().menus)
        return QSize(self.i_size.width, height)
    
    def helpEvent(self, ev, view, option, index):
        return QStyledItemDelegate.helpEvent(self, ev, view, option, index) # tooltip 感觉没什么用
        if not ev or not view:
            return False
        if ev.type() == ev.ToolTip:
            rect = view.visualRect(index)
            size = self.sizeHint(option, index)
            item=index.data(Qt.DisplayRole)
            tooltip = f"{item.title}\n\n{item.subTitle}"
            QToolTip.showText(ev.globalPos(), tooltip, view)
            return True
        return QStyledItemDelegate.helpEvent(self, ev, view, option, index)

