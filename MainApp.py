import sys
from functools import partial

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from GUI.MainWindow import Ui_MainWindow
from GUI.selectComponentWindow import Ui_ComponentSelectWindow
from GUI.configSecurityWindow import Ui_configSecurityWindow
from GUI.selectSingleComponentWindow import Ui_SingleComponentSelectWindow

from Optimizer import *

import datetime

import FileHandler
import json

ComponentsSelectedPT = {
    'Capacitors': 'Capacitores Selecionados',
    'Switches': 'Chaves Selecionadas',
    'Cores': 'Núcleos Selecionados',
    'Cables': 'Cabos Selecionados',
    'Diodes': 'Diodos Selecionados',
}

class Aplicativo(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Aplicativo, self).__init__(parent)
        self.setupUi(self)
        self.connect_actions()

        # Load general info.
        self.cores_database = FileHandler.load_all_cores()
        self.cables_database = FileHandler.load_all_cables()
        self.switches_database = FileHandler.load_all_switches()
        self.capacitors_database = FileHandler.load_all_capacitors()
        self.diodes_database = FileHandler.load_all_diodes()

        self.converter_configured = True
        self.security_params_configured = True

        self.available_components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': [],
        }
        self.selected_components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': [],
        }

        self.available_components_specific = {
            'C1': [],
            'C2': [],
            'C3': [],
            'C4': [],
            'D3': [],
            'D4': [],
            'S1': [],
            'S2': [],
            'LiCore': [],
            'LiCable': [],
            'LkCore': [],
            'LkCable': [],
            'TrPrimaryCable': [],
            'TrSecondaryCable': [],
            'TrCore': []
        }

        self.selected_components_specific = {
            'C1': None,
            'C2': None,
            'C3': None,
            'C4': None,
            'D3': None,
            'D4': None,
            'S1': None,
            'S2': None,
            'LiCore': None,
            'LiCable': None,
            'LkCore': None,
            'LkCable': None,
            'TrPrimaryCable': None,
            'TrSecondaryCable': None,
            'TrCore': None
        }
        self.selected_components_specifc = {}
        for name in self.capacitors_database:
            self.available_components['Capacitors'].append(name)
            print(self.capacitors_database[name].Vmax)
        for name in self.switches_database:
            self.available_components['Switches'].append(name)
        for name in self.cores_database:
            self.available_components['Cores'].append(name)
        for name in self.cables_database:
            self.available_components['Cables'].append(name)
        for name in self.diodes_database:
            self.available_components['Diodes'].append(name)

        # Variable needed to open a new window in the app.
        self.window = None

        # Variables need to open and handle selected components.
        self.model_available = None
        self.model_selected = None
        self.selected_item = None
        self.component_being_selected = None
        self.select_component_window = None
        self.config_security_window = None
        self.select_specific_component_window = None

        self.select_single_component_viewport = QtWidgets.QMainWindow()
        self.select_single_component_window = Ui_SingleComponentSelectWindow()
        self.select_single_component_window.setupUi(self.select_single_component_viewport)
        self.select_single

        self.circuit_features = {
            'Vo': 0.0,
            'Vi': 0.0,
            'dIin_max': 0.0,
            'dVo_max': 0.0,
            'Po': 0.0,
            'Jmax': 0.0,
            'Ro': 0.0
        }
        self.circuit_features_input_table = {
            'Vo': self.input_Vo,
            'Vi': self.input_Vin,
            'dIin_max': self.input_DeltaIin,
            'dVo_max': self.input_DeltaVo,
            'Po': self.input_Po,
            'Jmax': self.input_JMax
        }

        self.safety_window = QtWidgets.QMainWindow()
        self.config_security_window = Ui_configSecurityWindow()
        self.config_security_window.setupUi(self.safety_window)
        self.config_security_window.save_configurations_button.clicked.connect(self.save_security_configurations)
        self.safety_params = {
            'Vc': 2.0,
            'Vd': 2.0,
            'Id': 2.0,
            'Ic': 2.0,
            'ku': {'Transformer': 0.4, 'EntranceInductor': 0.4, 'AuxiliaryInductor': 0.4}
        }
        self.safety_params_input_table = {
            'Vc': self.config_security_window.input_fvcmax,
            'Vd': self.config_security_window.input_fvdmax,
            'Id': self.config_security_window.input_fidmax,
            'Ic': self.config_security_window.input_ficmax,
            'ku': {'Transformer': self.config_security_window.input_futrafo, 'EntranceInductor': self.config_security_window.input_fuLi, 'AuxiliaryInductor': self.config_security_window.input_fuLk}
        }
        for feature in self.safety_params:
            if type(self.safety_params_input_table[feature]) is dict:
                for secondary_feature in self.safety_params_input_table[feature]:
                    self.safety_params_input_table[feature][secondary_feature].setText(
                        str(self.safety_params[feature][secondary_feature]))
            else:
                self.safety_params_input_table[feature].setText(str(self.safety_params[feature]))

        aux = "config{:%m%d%Y}"
        self.default_file_name = aux.format(datetime.datetime.today())

        print("App Started")

    def optimize(self):
        if self.converter_configured:
            optimizer = GeneticOptimizer(self.get_components(), self.circuit_features, self.safety_params)
        else:
            if not self.converter_configured and not self.security_params_configured:
                warning = QMessageBox()
                warning.setWindowTitle("ATENÇÃO!")
                warning.setText("O conversor e os parâmetros de segurança não foram configurados")
                warning.setIcon(QMessageBox.Warning)
                warning.exec_()
            elif not self.converter_configured:
                warning = QMessageBox()
                warning.setWindowTitle("ATENÇÃO!")
                warning.setText("O conversor não foi configurado")
                warning.setIcon(QMessageBox.Warning)
                warning.exec_()
            elif not self.security_params_configured:
                warning = QMessageBox()
                warning.setWindowTitle("ATENÇÃO!")
                warning.setText("Os parâmetros de segurança não foram configurados")
                warning.setIcon(QMessageBox.Warning)
                warning.exec_()

    def save_circuit_features(self):
        try:
            for feature in self.circuit_features_input_table:
                if type(self.circuit_features_input_table[feature]) is dict:
                    for secondary_feature in self.circuit_features_input_table[feature]:
                        self.circuit_features[feature][secondary_feature] = float(self.circuit_features_input_table[feature][secondary_feature].text())
                else:
                    self.circuit_features[feature] = float(self.circuit_features_input_table[feature].text())
            self.circuit_features['Ro'] = (self.circuit_features['Vo']**2)/self.circuit_features['Po']
            self.converter_configured = True
        except:
            self.converter_configured = False
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO!")
            warning.setText("Uma ou mais entradas não foram configuradas")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()

    def create_file(self):
        print(str(float(self.circuit_features_input_table['Vo'].text())) + 'oi')
        print("Criar novo arquivo")

    # Saves all current configurations as a JSon File.
    def save_file(self):
        filename = QFileDialog.getSaveFileName(self, "Save File", self.default_file_name+'.json', filter='*.json')
        if filename[0]:
            with open(filename[0], 'w') as write_file:
                saved_data = [self.selected_components, self.available_components, self.safety_params, self.circuit_features]
                json.dump(saved_data, write_file, indent=2)

    # Reads configurations from a JSon File.
    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, "Open File", filter='*.json')
        self.read_file(filename[0])

    def read_file(self, filename):
        if filename:
            with open(filename, "r") as read_file:
                print(filename)
                data = json.load(read_file)
                self.selected_components = data[0]
                self.available_components = data[1]
                self.safety_params = data[2]
                self.circuit_features = data[3]
                for feature in self.circuit_features:
                    if feature in self.circuit_features_input_table:
                        if type(self.circuit_features_input_table[feature]) is dict:
                            for secondary_feature in self.circuit_features_input_table[feature]:
                                if self.circuit_features[feature][secondary_feature] != 0.0:
                                    self.circuit_features_input_table[feature][secondary_feature].setText(str(self.circuit_features[feature][secondary_feature]))
                        elif self.circuit_features[feature] != 0.0:
                            self.circuit_features_input_table[feature].setText(str(self.circuit_features[feature]))
                for feature in self.safety_params:
                    if type(self.safety_params_input_table[feature]) is dict:
                        for secondary_feature in self.safety_params_input_table[feature]:
                            self.safety_params_input_table[feature][secondary_feature].setText(str(self.safety_params[feature][secondary_feature]))
                    else:
                        self.safety_params_input_table[feature].setText(str(self.safety_params[feature]))

    def open_security_config_window(self):
        self.safety_window.show()

    def save_security_configurations(self):
        try:
            for feature in self.safety_params_input_table:
                if type(self.safety_params_input_table[feature]) is dict:
                    for secondary_feature in self.safety_params_input_table[feature]:
                        self.safety_params[feature][secondary_feature] = float(self.safety_params_input_table[feature][secondary_feature].text())
                else:
                    self.safety_params[feature] = float(self.safety_params_input_table[feature].text())
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
        self.select_component_window.label.setText(ComponentsSelectedPT[component_being_selected])

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

    def open_select_single_component_window(self, component_being_selected):
        self.selected_item = None

        self.component_being_selected = component_being_selected
        self.window = QtWidgets.QMainWindow()
        self.select_component_window = Ui_ComponentSelectWindow()
        self.select_component_window.setupUi(self.window)
        self.select_component_window.add_button.clicked.connect(self.add_component)
        self.select_component_window.remove_button.clicked.connect(self.remove_component)
        self.select_component_window.label.setText(ComponentsSelectedPT[component_being_selected])

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
        self.optimize_button.clicked.connect(self.optimize)
        self.pushButtonCableSel.clicked.connect(partial(self.open_select_component_window, 'Cables'))
        self.pushButtonCapSel.clicked.connect(partial(self.open_select_component_window, 'Capacitors'))
        self.pushButtonCoreSel.clicked.connect(partial(self.open_select_component_window, 'Cores'))
        self.pushButtonDiodeSel.clicked.connect(partial(self.open_select_component_window, 'Diodes'))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "Switches"))

        self.pushButtonCableSel.clicked.connect(partial(self.open_select_component_window, 'C1'))
        self.pushButtonCapSel.clicked.connect(partial(self.open_select_component_window, 'C2'))
        self.pushButtonCoreSel.clicked.connect(partial(self.open_select_component_window, 'C3'))
        self.pushButtonDiodeSel.clicked.connect(partial(self.open_select_component_window, 'C4'))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "D3"))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "D4"))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "S1"))
        self.pushButtonSwitchSel.clicked.connect(partial(self.open_select_component_window, "S2"))

        self.actionNew.triggered.connect(self.create_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSecurityConfig.triggered.connect(self.open_security_config_window)

    def get_components(self):
        components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': []
        }
        for name in self.selected_components['Capacitors']:
            components['Capacitors'].append(self.capacitors_database[name])
        for name in self.selected_components['Switches']:
            components['Switches'].append(self.switches_database[name])
        for name in self.selected_components['Cores']:
            components['Cores'].append(self.cores_database[name])
        for name in self.selected_components['Cables']:
            components['Cables'].append(self.cables_database[name])
        for name in self.selected_components['Diodes']:
            components['Diodes'].append(self.diodes_database[name])
        return components


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = Aplicativo()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
