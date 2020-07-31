import sys
from functools import partial

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GUI.MainWindow import Ui_MainWindow
from GUI.selectComponentWindow import Ui_ComponentSelectWindow
from GUI.configSecurityWindow import Ui_configSecurityWindow

from FileHandler import *


class Aplicativo(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Aplicativo, self).__init__(parent)
        self.setupUi(self)
        self.connect_actions()
        self.cores_database = load_all_cores()
        self.cables_database = load_all_cables()
        self.switches_database = load_all_switches()
        self.capacitors_database = load_all_capacitors()
        self.diodes_database = load_all_diodes()
        self.dissipators_database = load_all_dissipators()

        self.converter_configured = False
        self.security_params_configured = False

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
        self.config_security_window = None

        self.circuit_features = None
        self.safety_params = None

        print("Built")

    def save_circuit_features(self):
        try:
            vo = float(self.input_Vo.text())
            vin_min = float(self.input_VinMin.text())
            vin = float(self.input_Vin.text())
            vin_max = float(self.input_VinMax.text())
            d_in = float(self.input_DeltaIin.text())
            po = float(self.input_Vo.text())
            ro = (vo**2)/po
            d_vo = float(self.input_DeltaVo.text())
            circuit_features = {
                'Vo': vo,
                'D': {'Nominal': 0.55},
                'Vi': {'Min': vin_min, 'Nominal': vin, 'Max': vin_max},
                'dIin_max': d_in,
                'dVo_max': d_vo,
                'Ro': ro,
                'Po': po
            }
            self.circuit_features = circuit_features
            self.converter_configured = True
        except:
            self.converter_configured = False
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

    def open_security_config_window(self):
        self.window = QtWidgets.QMainWindow()
        self.config_security_window = Ui_configSecurityWindow()
        self.config_security_window.setupUi(self.window)
        self.config_security_window.save_configurations_button.clicked.connect(self.save_security_configurations)
        self.window.show()

    def save_security_configurations(self):
        try:
            fvcmax = float(self.config_security_window.input_fvcmax.text())
            fvdmax = float(self.config_security_window.input_fvdmax.text())
            ficmax = float(self.config_security_window.input_ficmax.text())
            fidmax = float(self.config_security_window.input_fidmax.text())
            futrafo = float(self.config_security_window.input_futrafo.text())
            fuLi = float(self.config_security_window.input_fuLi.text())
            fuLk = float(self.config_security_window.input_fuLk.text())
            safety_params = {
                'Vc1': fvcmax,
                'Vc2': fvcmax,
                'Vco': fvcmax,
                'Vdo': fvdmax,
                'Id': ficmax,
                'Ic': fidmax,
                'ku': {'Transformer': futrafo, 'EntranceInductor': fuLi, 'AuxiliaryInductor': fuLk}
            }
            self.safety_params = safety_params
            self.security_params_configured = True
        except:
            self.security_params_configured = False
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO!")
            warning.setText("Uma ou mais entradas não foram configuradas")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()

    def open_select_component_window(self, component_being_selected):
        self.selected_item = None

        self.component_being_selected = component_being_selected
        self.window = QtWidgets.QMainWindow()
        self.select_component_window = Ui_ComponentSelectWindow()
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


    def connect_actions(self):
        self.pushButtonCreateConverter.clicked.connect(self.save_circuit_features)
        self.pushButtonCableSel.clicked.connect(partial(self.open_select_component_window, 'Cables'))
        self.pushButtonCapSel.clicked.connect(partial(self.open_select_component_window, 'Capacitors'))
        self.pushButtonCoreSel.clicked.connect(partial(self.open_select_component_window, 'Cores'))
        self.pushButtonDiodeSel.clicked.connect(partial(self.open_select_component_window, 'Diodes'))
        self.pushButtonDissSel.clicked.connect(partial(self.open_select_component_window, 'Disspators'))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "Switches"))

        self.actionNew.triggered.connect(self.create_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSecurityConfig.triggered.connect(self.open_security_config_window)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = Aplicativo()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
