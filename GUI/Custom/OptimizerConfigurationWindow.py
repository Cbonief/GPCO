from PyQt5.QtWidgets import *

from GUI.Custom.FeatureExtractor import FeatureExtractor
from GUI.Custom.configOptimizerWindow import Ui_ConfigOptimizerWindow

DEFAULT_CONFIG = {
    'Epochs': 100,
    'Population Size': 100,
    'Mutation Rate': 0.5,
    'Rewrite Rate': 0.25,
    'Iterations': 100,
    'Tries': 3,
    'Method': 'SLSQP'
}

GA_CONFIG_KEYS = ['Epochs', 'Population Size', 'Mutation Rate', 'Rewrite Rate']
OPT_CONFIG_KEYS = ['Iterations', 'Tries', 'Method']


class OptimizerConfigurationWindow(Ui_ConfigOptimizerWindow):
    def __init__(self):
        super(OptimizerConfigurationWindow, self).__init__()

        self.viewport = QMainWindow()
        self.setupUi(self.viewport)

        self.parameters = DEFAULT_CONFIG

        self.optimizer_params_input_table = {
            'Epochs': self.input_epochs,
            'Population Size': self.input_pop_size,
            'Mutation Rate': self.input_mutation_rate,
            'Rewrite Rate': self.input_overwrite_rate,
            'Iterations': self.input_iterations,
            'Tries': self.input_tries,
            'Method': self.method_selector
        }

        self.parameters_handler = FeatureExtractor(self.optimizer_params_input_table)
        self.parameters_handler.set_features(self.parameters)

        self.save_configurations_button.clicked.connect(self.save_configuration)

    def open_window(self):
        self.viewport.setWindowTitle('Configuração do Otimizador')
        self.viewport.show()

    def set_features(self, features):
        self.parameters_handler.set_features(features)

    def get_features(self):
        return self.parameters_handler.get_features()

    def get_ga_config(self):
        return {key: self.parameters_handler.get_feature(key) for key in GA_CONFIG_KEYS}

    def get_opt_config(self):
        return {key: self.parameters_handler.get_feature(key) for key in OPT_CONFIG_KEYS}

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
