import sys

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy as np

from MainWindow import Ui_MainWindow
from selectCapWindow import Ui_selectCapWindow

from FileHandler import *

import BoostHalfBridge

class Aplicativo(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Aplicativo, self).__init__(parent)
        self.setupUi(self)
        self.connectActions()
        self.cores_database = loadCores()
        self.cables_database = loadCables()
        self.switches_database = loadSwitches()
        self.capacitors_database = loadCapacitors()
        self.diodes_database = loadDiodes()
        self.dissipators_database = loadDissipators()
        self.available_capacitors = []
        for name in self.capacitors_database:
            self.available_capacitors.append(name)
        self.selected_capacitors = []

        print("Built")

    x = 3
    x = 2

    def Optimize(self):
        try:
            user_input = [
                float(self.input_Vin.text()),
                float(self.input_Vo.text()),
                float(self.input_DeltaVo.text()),
                float(self.input_DeltaIin.text()),
                float(self.input_Po.text())
            ]
        except:
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO!")
            warning.setText("Uma ou mais entradas não foram configuradas")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()
        finally:
            circuit_features = {
                'Vo': user_input[1],
                'D': {'Nominal': 0.55},
                'Vi': user_input[0],
                'dIin_max': user_input[3],
                'Ro': (user_input[1]**2/user_input[4]),
                'Po': user_input[4],
                'Bmax': {'Transformer': 0.15}
            }
            print(circuit_features)

    def createFile(self):
        print("Criar novo arquivo")

    def saveFile(self):
        print("Salvar arquivo")

    def openFile(self):
        print("Abrir arquivo")

    def selectCables(self):
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([1, 4, 9, 16, 25])
        self.graphWidget.plot(x,y,"X ao quadrado", "x2")
        print("SelectCables")

    def selectCapacitors(self):
        print("SelectCapacitors")
        self.window = QtWidgets.QMainWindow()
        self.select_cap = Ui_selectCapWindow()
        self.select_cap.setupUi(self.window)
        self.select_cap.add_button.clicked.connect(self.add_capacitor)
        model = QStandardItemModel(self.select_cap.list_available)
        for name in self.available_capacitors:
            item = QStandardItem(name)
            model.appendRow(item)
        self.select_cap.list_available.setModel(model)
        model = QStandardItemModel(self.select_cap.list_selected)
        for name in self.selected_capacitors:
            item = QStandardItem(name)
            model.appendRow(item)
        self.select_cap.list_selected.setModel(model)
        self.window.show()

    def add_capacitor(self):
        selected = self.select_cap.list_available.selectedIndexes()
        for element in selected:
            print(element.data(role = QtD))
        #model = QStandardItemModel(self.select_cap.list_available)
        #for name in self.available_capacitors:
        #    item = QStandardItem(name)
        #    model.appendRow(item)
        #self.select_cap.list_available.setModel(model)
        #model = QStandardItemModel(self.select_cap.list_selected)
        #for name in self.select_capacitors:
        #    item = QStandardItem(name)
        #    model.appendRow(item)
        #self.select_cap.list_selected.setModel(model)

    def selectSwitches(self):
        print("SelectSwitches")

    def selectDissipators(self):
        print("SelectDissipators")

    def selectDiodes(self):
        print("SelectDiodes")

    def selectCores(self):
        print("SelectCores")

    def connectActions(self):
        self.pushButtonOptimize.clicked.connect(self.Optimize)
        self.pushButtonCableSel.clicked.connect(self.selectCables)
        self.pushButtonCapSel.clicked.connect(self.selectCapacitors)
        self.pushButtonCoreSel.clicked.connect(self.selectCores)
        self.pushButtonDiodeSel.clicked.connect(self.selectDiodes)
        self.pushButtonDissSel.clicked.connect(self.selectDissipators)
        self.pushButtonSwitchSel.clicked.connect(self.selectSwitches)

        self.actionNew.triggered.connect(self.createFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionOpen.triggered.connect(self.openFile)

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = Aplicativo()
    form.show()
    form.update() #start with something
    app.exec_()
    print("DONE")
