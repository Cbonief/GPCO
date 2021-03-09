import datetime
import json
import sys

from PyQt5.QtWidgets import *

from Converter.BoostHalfBridge import BoostHalfBridgeInverter
from GUI.Custom.PopUpWindow import warning
from Main import MainWindow
from Optimizer.Continuous import optimize_converter
from Optimizer.CustomUtilization import optimize_components


class OptimizationMode:
    COMPLETE = 0
    CONTINUOUS_ONLY = 1


class Aplicativo(MainWindow):
    def __init__(self):
        super(Aplicativo, self).__init__()

        # self.circuit_features_handler = FeatureExtractor(
        #     {
        #         'Vo': self.input_Vo,
        #         'Vi': self.input_Vin,
        #         'dIin_max': self.input_DeltaIin,
        #         'dVo_max': self.input_DeltaVo,
        #         'Po': self.input_Po,
        #         'Jmax': self.input_JMax
        #     },
        #     {'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15}, 'dVc1': 0.10, 'dVc2': 0.10}
        # )

        aux = "config{:%m%d%Y}"
        self.default_file_name = aux.format(datetime.datetime.today())

        print("App Started")

        self.optimization_mode = OptimizationMode.CONTINUOUS_ONLY

        # self.connect_actions()

    def optimize(self):
        a = self.circuit_features_handler.is_ready()
        b = self.security_configuration.is_configured()
        c = False
        # selected_components_keys, components_data_base, design_features, safety_parameters, ga_config = None, num_opt_config = None

        if self.optimization_mode == OptimizationMode.COMPLETE:
            c = self.multi_component_selector.all_configured()
        elif self.optimization_mode == OptimizationMode.CONTINUOUS_ONLY:
            c = self.single_component_selector.all_configured()

        if a and b and c:
            # Is ready to start the optimization.
            if self.optimization_mode == OptimizationMode.COMPLETE:
                optimized_convereter = optimize_components()

            elif self.optimization_mode == OptimizationMode.CONTINUOUS_ONLY:

                converter = BoostHalfBridgeInverter()
                [result, sucess, output] = optimize_converter(converter, epochs=100, subroutine_iteration=1000)
        else:
            warning("Conversor não configurado")

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
        print("({},{})".format(self.width(), self.height()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = Aplicativo()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
