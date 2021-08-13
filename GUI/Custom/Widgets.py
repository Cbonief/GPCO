from PyQt5.QtWidgets import QSpacerItem, QHBoxLayout, QSizePolicy, QLabel, QLineEdit


class LabeledInput(QHBoxLayout):
    def __init__(self, name, spacing=None, parent=None):
        super().__init__()
        if spacing is None:
            spacing = [20, 40]
        self.parent = parent
        self.addItem(QSpacerItem(spacing[0], 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        name_label = QLabel(name + ":")
        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        name_label.setFixedSize(150, 20)
        self.addWidget(name_label)
        self.input_edit = QLineEdit()
        self.input_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.input_edit.setFixedSize(50, 20)
        self.addWidget(self.input_edit)
        self.addItem(QSpacerItem(spacing[1], 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

    def value(self):
        return float(self.input_edit.text())

    def set_value(self, value):
        self.input_edit.setText(str(value))


class CenteredWidget(QHBoxLayout):
    def __init__(self, widget):
        super().__init__()
        self.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.addWidget(widget)
        self.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))


class SpacedWidget(QHBoxLayout):
    def __init__(self, widgets):
        super().__init__()
        self.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for i in range(0, len(widgets)):
            widget = widgets[i]
            widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            self.addWidget(widget)
            if i < len(widgets) - 1:
                self.addItem(QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))
        self.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
