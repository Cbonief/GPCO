import sys
from functools import partial

from PyQt5 import QtWidgets
from PyQt5.QtCore import QModelIndex, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

from GUI.MainWindow import Ui_MainWindow
from GUI.selectCapWindow import Ui_selectCapWindow

from FileHandler import *


class Aplicativo(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Aplicativo, self).__init__(parent)
        self.setupUi(self)
        self.connectActions()
        self.cores_database = load_all_cores()
        self.cables_database = load_all_cables()
        self.switches_database = load_all_switches()
        self.capacitors_database = load_all_capacitors()
        self.diodes_database = load_all_diodes()
        self.dissipators_database = load_all_dissipators()

        self.available_components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': [],
            'Dissipators': []
        }
        self.selected_components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': [],
            'Dissipators': []
        }
        for name in self.capacitors_database:
            self.available_components['Capacitors'].append(name)
        for name in self.switches_database:
            self.available_components['Switches'].append(name)
        for name in self.cores_database:
            self.available_components['Cores'].append(name)
        for name in self.cables_database:
            self.available_components['Cables'].append(name)
        for name in self.diodes_database:
            self.available_components['Diodes'].append(name)
        for name in self.dissipators_database:
            self.available_components['Dissipators'].append(name)

        # Variable needed to open a new window in the app.
        self.window = None

        # Variables need to open and handle selected components.
        self.model_available = None
        self.model_selected = None
        self.selected_item = None
        self.component_being_selected = None
        self.select_component_window = None

        print("Built")

    def optimize(self):
        try:
            user_input = [
                float(self.input_Vin.text()),
                float(self.input_Vo.text()),
                float(self.input_DeltaVo.text()),
                float(self.input_DeltaIin.text()),
                float(self.input_Po.text())
            ]
            circuit_features = {
                'Vo': user_input[1],
                'D': {'Nominal': 0.55},
                'Vi': user_input[0],
                'dIin_max': user_input[3],
                'Ro': (user_input[1] ** 2 / user_input[4]),
                'Po': user_input[4],
                'Bmax': {'Transformer': 0.15}
            }
        except NameError:
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO!")
            warning.setText("Uma ou mais entradas não foram configuradas")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()

    def create_file(self):
        print("Criar novo arquivo")

    def save_file(self):
        print("Salvar arquivo")

    def open_file(self):
        print("Abrir arquivo")

    def selectCables(self):
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([1, 4, 9, 16, 25])
        self.graphWidget.plot(x, y, "X ao quadrado", ['x2'], ['x', 'y'])
        print("SelectCables")

    def open_select_component_window(self, component_being_selected):
        print(component_being_selected)
        self.selected_item = None

        self.component_being_selected = component_being_selected
        self.window = QtWidgets.QMainWindow()
        self.select_component_window = Ui_selectCapWindow()
        self.select_component_window.setupUi(self.window)
        self.select_component_window.add_button.clicked.connect(self.add_component)
        self.select_component_window.remove_button.clicked.connect(self.remove_component)
        self.select_component_window.label.setText('Selecionados')

        self.model_available = QStandardItemModel(self.select_component_window.list_available)
        for name in self.available_components[component_being_selected]:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model_available.appendRow(item)
        self.select_component_window.list_available.setModel(self.model_available)
        try:
            self.select_component_window.list_available.clicked.connect(self.component_available_clicked)
        finally:
            self.model_selected = QStandardItemModel(self.select_component_window.list_selected)
            for name in self.selected_components[component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.select_component_window.list_selected.setModel(self.model_selected)
            try:
                self.select_component_window.list_selected.clicked.connect(self.component_selected_clicked)
            finally:
                self.window.show()

    def component_available_clicked(self, index):
        self.selected_item = self.model_available.itemFromIndex(index)

    def component_selected_clicked(self, index):
        self.selected_item = self.model_selected.itemFromIndex(index)

    def add_component(self):
        if self.selected_item is not None:
            self.available_components[self.component_being_selected].remove(self.selected_item.text())
            self.selected_components[self.component_being_selected].append(self.selected_item.text())
            self.model_available = QStandardItemModel(self.select_component_window.list_available)
            for name in self.available_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_available.appendRow(item)
            self.select_component_window.list_available.setModel(self.model_available)

            self.model_selected = QStandardItemModel(self.select_component_window.list_selected)
            for name in self.selected_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.select_component_window.list_selected.setModel(self.model_selected)
            self.select_component_window.list_selected.clicked.connect(self.component_selected_clicked)
            self.selected_item = None

    def remove_component(self):
        if self.selected_item is not None:
            self.available_components[self.component_being_selected].append(self.selected_item.text())
            self.selected_components[self.component_being_selected].remove(self.selected_item.text())
            self.model_available = QStandardItemModel(self.select_component_window.list_available)
            for name in self.available_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_available.appendRow(item)
            self.select_component_window.list_available.setModel(self.model_available)

            self.model_selected = QStandardItemModel(self.select_component_window.list_selected)
            for name in self.selected_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.select_component_window.list_selected.setModel(self.model_selected)
            self.selected_item = None

    def selectSwitches(self):

        self.window = QtWidgets.QMainWindow()
        self.select_component_window = Ui_selectCapWindow()
        self.select_component_window.setupUi(self.window)
        self.select_component_window.add_button.clicked.connect(self.add_capacitor)
        self.select_component_window.remove_button.clicked.connect(self.remove_capacitor)
        self.select_component_window.label.setText('Chaves Selecionadas')

        self.model_available = QStandardItemModel(self.select_component_window.list_available)
        for name in self.available_switches:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model_available.appendRow(item)
        self.select_component_window.list_available.setModel(self.model_available)
        self.select_component_window.list_available.clicked.connect(self.component_available_clicked)

        self.model_selected = QStandardItemModel(self.select_component_window.list_selected)
        for name in self.selected_capacitors:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model_selected.appendRow(item)
        self.select_component_window.list_selected.setModel(self.model_selected)

        self.window.show()

    def selectDissipators(self):
        print("SelectDissipators")

    def selectDiodes(self):
        print("SelectDiodes")

    def selectCores(self):
        self.component_being_selected

    def connectActions(self):
        self.pushButtonOptimize.clicked.connect(self.optimize)
        self.pushButtonCableSel.clicked.connect(partial(self.open_select_component_window, 'Cables'))
        self.pushButtonCapSel.clicked.connect(partial(self.open_select_component_window, 'Capacitors'))
        self.pushButtonCoreSel.clicked.connect(partial(self.open_select_component_window, 'Cores'))
        self.pushButtonDiodeSel.clicked.connect(partial(self.open_select_component_window, 'Diodes'))
        self.pushButtonDissSel.clicked.connect(partial(self.open_select_component_window, 'Disspators'))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "Switches"))

        self.actionNew.triggered.connect(self.create_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOpen.triggered.connect(self.open_file)

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = Aplicativo()
    form.show()
    form.update() #start with something
    app.exec_()
    print("DONE")
