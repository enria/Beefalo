from PyQt5 import Qt, QtCore
from PyQt5.QtCore import QSize, QRect, QPoint
from PyQt5.QtGui import QPixmap, QColor, QBrush, QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import QStyledItemDelegate


class WidgetDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        pm = QPixmap("images//" + index.data().icon)
        pm = pm.scaled(32, 32, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        if index.data().selected:
            background_brush = QBrush(QColor("#4f6180"), QtCore.Qt.SolidPattern)
            painter.fillRect(option.rect, background_brush)

        font = QFont('微软雅黑', 12)
        font.setWeight(60)
        SubFont = QFont('微软雅黑', 9)
        SubFont.setWeight(SubFont.weight() - 2)

        icon = QIcon(pm)
        headerText = index.data().title
        subText = index.data().subTitle
        iconsize = QSize(32, 32);

        iconRect = QRect(7, option.rect.top() + 7, 32, 32)
        headerRect = QRect(48, iconRect.top() - 3, option.rect.width() - 48, 21)
        subheaderRect = QRect(48, iconRect.top() + 18, option.rect.width() - 48, 16)

        painter.drawPixmap(
            QPoint(iconRect.left(), iconRect.top()),
            icon.pixmap(iconsize.width(), iconsize.height()));
        painter.setFont(font);
        painter.setPen(QColor("#f5f6f1"))
        painter.drawText(headerRect, QtCore.Qt.AlignTop, headerText);

        painter.setFont(SubFont);
        painter.setPen(QColor("#d9d9d4"))
        painter.drawText(subheaderRect, QtCore.Qt.AlignTop, subText)
        # painter.restore()

    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QSize:
        return QSize(100, 46)
