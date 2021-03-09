from PyQt5.QtWidgets import *

from GUI.Custom.FeatureExtractor import FeatureExtractor
from GUI.Custom.configSecurityWindow import Ui_ConfigSecurityWindow

DEFAULT_CONFIG = {
    'Vc': 2.0,
    'Vd': 2.0,
    'Vs': 2.0,
    'Id': 2.0,
    'Ic': 2.0,
    'Is': 2.0,
    'ku Transformer': 0.4,
    'ku EntranceInductor': 0.4,
    'ku AuxiliaryInductor': 0.4,
    'Jmax': 450
}


class SecurityConfigurationWindow(Ui_ConfigSecurityWindow):
    def __init__(self):
        super(SecurityConfigurationWindow, self).__init__()

        self.viewport = QMainWindow()
        self.setupUi(self.viewport)

        self.parameters = DEFAULT_CONFIG

        self.safety_params_input_table = {
            'Vc': self.input_fvcmax,
            'Vd': self.input_fvdmax,
            'Vs': self.input_fvsmax,
            'Id': self.input_fidmax,
            'Ic': self.input_ficmax,
            'Is': self.input_ismax,
            'ku Transformer': self.input_futrafo,
            'ku EntranceInductor': self.input_fuLi,
            'ku AuxiliaryInductor': self.input_fuLk,
            'Jmax': self.input_Jmax
        }
        self.label.setText("Parâmetros de Segurança")

        self.parameters_handler = FeatureExtractor(self.safety_params_input_table)
        self.parameters_handler.set_features(self.parameters)

        self.save_configurations_button.clicked.connect(self.save_configuration)

    def open_window(self):
        self.viewport.setWindowTitle('Parâmetros de Segurança')
        self.viewport.show()

    def set_parameters(self, features):
        self.parameters_handler.set_features(features)

    def get_parameters(self):
        return self.parameters_handler.get_features()

    def save_configuration(self):
        for key in self.parameters.keys():
            if self.parameters_handler.is_filled(key):
                self.parameters[key] = self.parameters_handler.get_feature(key)
            else:
                self.parameters[key] = DEFAULT_CONFIG[key]
                self.parameters_handler.set_feature(key, DEFAULT_CONFIG[key])

    def is_configured(self):
        return self.parameters_handler.is_ready()

    def reset_values(self):
        self.parameters = DEFAULT_CONFIG
