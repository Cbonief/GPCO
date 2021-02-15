from PyQt5.QtWidgets import QMessageBox
from functools import partial


class FeatureExtractor:

    def __init__(self, circuit_features_input_table, other_values=None):
        self.features = {}
        self.filled = {}
        self.number_of_features_filled = 0
        self.number_of_features = len(list(circuit_features_input_table.keys()))
        self.input_table = circuit_features_input_table
        for key in self.input_table:
            self.features[key] = 0
            self.filled[key] = False
            self.input_table[key].textChanged.connect(partial(self.store_feature_value, key))
        if other_values:
            for key in other_values:
                self.features[key] = other_values[key]
        self.finished = False

    def store_feature_value(self, key):
        try:
            self.features[key] = float(self.input_table[key].text())
        except ValueError:
            if self.filled[key]:
                self.filled[key] = False
                self.features[key] = 0.0
                self.number_of_features_filled -= 1
        if self.features[key] >= 0 and not self.filled[key]:
            self.number_of_features_filled += 1
            self.filled[key] = True
            self.finished = self.number_of_features_filled == self.number_of_features

    def get_user_input(self):
        try:
            for key in self.input_table:
                self.features[key] = float(self.input_table[key].text())
            self.finished = True
        except ValueError:
            self.finished = False
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO!")
            warning.setText("Uma ou mais entradas não foram configuradas")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()

    def get_features(self):
        return self.features

    def set_features(self, features):
        for key in features:
            self.features[key] = features[key]
            self.input_table[key].setText(str(features[key]))

    def is_ready(self):
        return self.finished
