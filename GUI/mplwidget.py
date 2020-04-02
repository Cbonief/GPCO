from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure


class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(vertical_layout)

    def plot(self, dataX, dataY, title, legend, labels):
        self.canvas.axes.clear()
        self.canvas.axes.plot(dataX, dataY)
        self.canvas.axes.set_xlabel(labels[0], fontsize=12)
        self.canvas.axes.set_ylabel(labels[1], fontsize=12)
        self.canvas.axes.legend(legend, loc='upper right')
        self.canvas.axes.set_title(title)
        self.canvas.draw()
