import copy
from functools import partial

from PyQt5.QtWidgets import *

from GUI.Custom.Widgets import LabeledInput


class InputType:
    TEXT = 0
    SPIN = 1
    COMBO = 2
    LABELED = 3


class FeatureExtractor:

    def __init__(self, circuit_features_input_table, other_values=None):
        self.features = {}
        self.filled = {}
        self.number_of_features_filled = 0
        self.number_of_features = len(list(circuit_features_input_table.keys()))
        self.input_table = circuit_features_input_table
        self.input_types = {}
        for key in self.input_table:
            self.features[key] = 0
            self.filled[key] = False
            input_widget = self.input_table[key]
            if isinstance(input_widget, QSpinBox):
                self.input_types[key] = InputType.SPIN
                self.number_of_features_filled += 1
                self.filled[key] = True
            elif isinstance(input_widget, QLineEdit):
                self.input_types[key] = InputType.TEXT
            elif isinstance(input_widget, QComboBox):
                self.input_types[key] = InputType.COMBO
                self.number_of_features_filled += 1
                self.filled[key] = True
            elif isinstance(input_widget, LabeledInput):
                self.input_types[key] = InputType.LABELED
            self.connect_widget(key, input_widget)

        if other_values:
            for key in other_values:
                self.features[key] = other_values[key]
        self.finished = False

    def store_feature_value(self, key):
        try:
            if self.input_types[key] == InputType.TEXT:
                self.features[key] = float(self.input_table[key].text())
            elif self.input_types[key] == InputType.SPIN:
                self.features[key] = self.input_table[key].value()
            elif self.input_types[key] == InputType.COMBO:
                self.features[key] = self.input_table[key].currentText()
            elif self.input_types[key] == InputType.LABELED:
                self.features[key] = self.input_table[key].value()

            if self.input_types[key] != InputType.COMBO and self.features[key] > 0 and not self.filled[key]:
                self.number_of_features_filled += 1
                self.filled[key] = True
        except ValueError:
            if self.filled[key]:
                self.filled[key] = False
                self.features[key] = 0.0
                self.number_of_features_filled -= 1
        self.finished = self.number_of_features_filled == self.number_of_features

    def get_features(self):
        return copy.deepcopy(self.features)

    def get_feature(self, key):
        try:
            return self.features[key]
        except KeyError:
            return False

    def set_features(self, features):
        for key in features:
            self.features[key] = features[key]
            if key in self.input_table:
                if self.input_types[key] == InputType.SPIN:
                    self.input_table[key].setValue(features[key])
                elif self.input_types[key] == InputType.TEXT:
                    self.input_table[key].setText(str(features[key]))
                elif self.input_types[key] == InputType.COMBO:
                    self.input_table[key].setCurrentText(features[key])
                elif self.input_types[key] == InputType.LABELED:
                    self.input_table[key].set_value(features[key])

    def set_feature(self, key, value):
        self.features[key] = value
        self.input_table[key].setText(str(value))

    def is_filled(self, key):
        try:
            return self.filled[key]
        except KeyError:
            return False

    def is_ready(self):
        return self.finished

    def connect_widget(self, key, widget):
        if self.input_types[key] == InputType.SPIN:
            widget.valueChanged.connect(partial(self.store_feature_value, key))
        elif self.input_types[key] == InputType.TEXT:
            widget.textChanged.connect(partial(self.store_feature_value, key))
        elif self.input_types[key] == InputType.COMBO:
            widget.currentTextChanged.connect(partial(self.store_feature_value, key))
        elif self.input_types[key] == InputType.LABELED:
            widget.input_edit.textChanged.connect(partial(self.store_feature_value, key))

    def reset_values(self):
        for key in self.features:
            self.features[key] = 0
            if key in self.input_table.keys():
                if self.input_types[key] == InputType.SPIN:
                    self.input_table[key].setValue(0)
                elif self.input_types[key] == InputType.TEXT:
                    self.input_table[key].setText(str(0))
                elif self.input_types[key] == InputType.COMBO:
                    self.input_table[key].setCurrentText(0)
                elif self.input_types[key] == InputType.LABELED:
                    self.input_table[key].set_value(0.0)
