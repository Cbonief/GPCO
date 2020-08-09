from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class CircuitView(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)

    def mouseDoubleClickEvent(self, event):
        print("Click")
        clicked_item = self.itemAt(event.pos())
        print(clicked_item)

