import datetime
import json
import sys
from functools import partial

from PyQt5.QtWidgets import *

from GUI.Handlers.FileHandler import ComponentsReader
from GUI.MainWindow import Ui_MainWindow
from GUI.Handlers.ComponentSelector import SingleComponentSelector, MultiComponentSelector
from GUI.Handlers.InductorCreator import InductorCreationHandler
from GUI.Handlers.TransformerCreator import TransformerCreationHandler
from GUI.Handlers.FeatureExtractor import FeatureExtractor
from GUI.SecurityConfigurationWindow import SecurityConfigurationWindow


class OptimizationMode:
    ComponentSelection = 0
    OperationPoint = 1


class Aplicativo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Aplicativo, self).__init__(parent)
        self.setupUi(self)

        components = ComponentsReader()

        # Loads all components
        available_components, available_components_specific = components.create_available_components_maps()
        self.single_component_selector = SingleComponentSelector(available_components_specific)
        self.multi_component_selector = MultiComponentSelector(available_components)
        inductors = ['Li', 'Lk']
        available_components_inductor = {component: available_components_specific[component] for component in inductors}
        self.inductor_creator = InductorCreationHandler(available_components_inductor, parent=self)
        self.transformer_creator = TransformerCreationHandler(available_components_specific['Transformer'], parent=self)

        self.security_window = SecurityConfigurationWindow()

        # Variable needed to open a new window in the app.
        self.window = None

        self.circuit_features = {
            'Vo': 0.0,
            'Vi': 0.0,
            'dIin_max': 0.0,
            'dVo_max': 0.0,
            'Po': 0.0,
            'Jmax': 0.0,
            'Ro': 0.0
        }
        # self.features['Bmax'] = {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15}
        # self.features['dVc1'] = 0.10
        # self.features['dVc2'] = 0.10

        circuit_features_input_table = {
            'Vo': self.input_Vo,
            'Vi': self.input_Vin,
            'dIin_max': self.input_DeltaIin,
            'dVo_max': self.input_DeltaVo,
            'Po': self.input_Po,
            'Jmax': self.input_JMax
        }

        self.circuit_features_handler = FeatureExtractor(circuit_features_input_table)

        self.safety_params = {
            'Vc': 2.0,
            'Vd': 2.0,
            'Id': 2.0,
            'Ic': 2.0,
            'ku': {'Transformer': 0.4, 'EntranceInductor': 0.4, 'AuxiliaryInductor': 0.4}
        }

        aux = "config{:%m%d%Y}"
        self.default_file_name = aux.format(datetime.datetime.today())

        print("App Started")

        self.converter_configured = False
        self.security_params_configured = False
        self.optimization_mode = OptimizationMode.ComponentSelection

        self.connect_actions()

    def optimize(self):
        if self.converter_configured:
            x=2
            # optimizer = GeneticOptimizer(self.get_components(), self.circuit_features, self.safety_params)
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


    def create_file(self):
        print(str(float(self.circuit_features_input_table['Vo'].text())) + 'oi')
        print("Criar novo arquivo")

    # Saves all current configurations as a JSon File.
    def save_file(self):
        filename = QFileDialog.getSaveFileName(self, "Save File", self.default_file_name + '.json', filter='*.json')
        if filename[0]:
            with open(filename[0], 'w') as write_file:
                saved_data = [self.selected_components, self.available_components, self.safety_params,
                              self.circuit_features]
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
                                    self.circuit_features_input_table[feature][secondary_feature].setText(
                                        str(self.circuit_features[feature][secondary_feature]))
                        elif self.circuit_features[feature] != 0.0:
                            self.circuit_features_input_table[feature].setText(str(self.circuit_features[feature]))
                for feature in self.safety_params:
                    if type(self.safety_params_input_table[feature]) is dict:
                        for secondary_feature in self.safety_params_input_table[feature]:
                            self.safety_params_input_table[feature][secondary_feature].setText(
                                str(self.safety_params[feature][secondary_feature]))
                    else:
                        self.safety_params_input_table[feature].setText(str(self.safety_params[feature]))

    def testFunction(self):
        print(self.tabWidget.currentIndex())

    def connect_actions(self):
        self.save_design_features.clicked.connect(self.circuit_features_handler.get_user_input)
        self.optimize_button.clicked.connect(self.optimize)

        self.pushButtonCableSel.clicked.connect(partial(self.multi_component_selector.open_window, 'Cables'))
        self.pushButtonCapSel.clicked.connect(partial(self.multi_component_selector.open_window, 'Capacitors'))
        self.pushButtonCoreSel.clicked.connect(partial(self.multi_component_selector.open_window, 'Cores'))
        self.pushButtonDiodeSel.clicked.connect(partial(self.multi_component_selector.open_window, 'Diodes'))
        self.pushButtonSwitchSel.clicked.connect(partial(self.multi_component_selector.open_window, "Switches"))

        self.pushButtonSelC1.clicked.connect(partial(self.single_component_selector.open_window, 'C1'))
        self.pushButtonSelC2.clicked.connect(partial(self.single_component_selector.open_window, 'C2'))
        self.pushButtonSelC3.clicked.connect(partial(self.single_component_selector.open_window, 'C3'))
        self.pushButtonSelC4.clicked.connect(partial(self.single_component_selector.open_window, 'C4'))
        self.pushButtonSelD3.clicked.connect(partial(self.single_component_selector.open_window, "D3"))
        self.pushButtonSelD4.clicked.connect(partial(self.single_component_selector.open_window, "D4"))
        self.pushButtonSelS1.clicked.connect(partial(self.single_component_selector.open_window, "S1"))
        self.pushButtonSelS2.clicked.connect(partial(self.single_component_selector.open_window, "S2"))

        self.pushButtonSelLi.clicked.connect(partial(self.inductor_creator.open_window, 'Li'))
        self.pushButtonSelLk.clicked.connect(partial(self.inductor_creator.open_window, 'Lk'))
        self.pushButtonSelTr.clicked.connect(self.transformer_creator.open_window)

        self.actionNew.triggered.connect(self.create_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionSecurityConfig.triggered.connect(self.security_window.open_window)

        self.testButton.clicked.connect(self.testFunction)

    def get_components(self):
        components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': []
        }
        for name in self.selected_components['Capacitors']:
            components['Capacitors'].append(self.capacitors[name])
        for name in self.selected_components['Switches']:
            components['Switches'].append(self.switches[name])
        for name in self.selected_components['Cores']:
            components['Cores'].append(self.cores[name])
        for name in self.selected_components['Cables']:
            components['Cables'].append(self.cables[name])
        for name in self.selected_components['Diodes']:
            components['Diodes'].append(self.diodes[name])
        return components


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = Aplicativo()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
