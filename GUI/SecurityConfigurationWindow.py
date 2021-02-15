from PyQt5.QtWidgets import *
from GUI.configSecurityWindow import Ui_configSecurityWindow
from GUI.Handlers.FeatureExtractor import FeatureExtractor


class SecurityConfigurationWindow(Ui_configSecurityWindow):
    def __init__(self):
        super(SecurityConfigurationWindow, self).__init__()

        self.viewport = QMainWindow()
        self.setupUi(self.viewport)

        self.safety_params = {
            'Vc': 2.0,
            'Vd': 2.0,
            'Id': 2.0,
            'Ic': 2.0,
            'ku Transformer': 0.4,
            'ku EntranceInductor': 0.4,
            'ku AuxiliaryInductor': 0.4
        }

        self.safety_params_input_table = {
            'Vc': self.input_fvcmax,
            'Vd': self.input_fvdmax,
            'Id': self.input_fidmax,
            'Ic': self.input_ficmax,
            'ku Transformer': self.input_futrafo,
            'ku EntranceInductor': self.input_fuLi,
            'ku AuxiliaryInductor': self.input_fuLk
        }

        self.parameters_handler = FeatureExtractor(self.safety_params_input_table)
        self.parameters_handler.set_features(self.safety_params)

    def open_window(self):
        self.viewport.setWindowTitle('Parâmetros de Segurança')
        self.viewport.show()

    def set_features(self, features):
        self.parameters_handler.set_features(features)

    def get_features(self, features):
        return self.parameters_handler.get_features()
