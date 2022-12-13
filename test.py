# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Window(QMainWindow):

	def __init__(self):
		super().__init__()

		# setting title
		self.setWindowTitle("Python ")

		# setting geometry
		self.setGeometry(100, 100, 600, 400)

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

	# method for widgets
	def UiComponents(self):

		# creating label
		label = QLabel("Label", self)

		# setting geometry to the label
		label.setGeometry(200, 100, 150, 60)

		# setting alignment to the label
		label.setAlignment(Qt.AlignCenter)

		# setting font
		label.setFont(QFont('Arial', 15))

		# setting style sheet of the label
		label.setStyleSheet("QLabel"
							"{"
							"border : 2px solid green;"
							"background : lightgreen;"
							"}")

		# creating a blur effect
		self.blur_effect = QGraphicsBlurEffect()


		# setting blur radius
		self.blur_effect.setBlurRadius(15)

		# adding blur effect to the label
		label.setGraphicsEffect(self.blur_effect)


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())

    # "<ctrl>+<1>": "tip ",
    # "<ctrl>+<3>": "find ",
    # "<ctrl>+<2>": "dict ",
    # "<ctrl>+<17>": "todo ",
    # "<ctrl>+<5>": "ghb ",
    # "<ctrl>+<12>": "qrc ",
    # "<ctrl>+<11>": "baidu ",
    # "<ctrl>+<9>": "vsc ",
    # "<ctrl>+<8>": "chbm ",
    # "<ctrl>+<45>": "notion "
