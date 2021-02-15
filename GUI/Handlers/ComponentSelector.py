from GUI.Handlers.selectComponentWindow import Ui_ComponentSelectWindow
from GUI.Handlers.selectSingleComponentWindow import Ui_SingleComponentSelectWindow
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

ENGLISH = 0
PORTUGUESE = 1

# with open('GUI/texts-pt_BR.json') as json_file:
#     print(json.load(json_file))

select_multi_component_label = {
    'Capacitors': 'Capacitores Selecionados',
    'Switches': 'Chaves Selecionadas',
    'Cores': 'Núcleos Selecionados',
    'Cables': 'Cabos Selecionados',
    'Diodes': 'Diodos Selecionados',
}

select_single_component_label = {
    'C1': 'Selecione C1',
    'C2': 'Selecione C2',
    'C3': 'Selecione C3',
    'C4': 'Selecione C4',
    'D3': 'Selecione D3',
    'D4': 'Selecione D4',
    'S1': 'Selecione S1',
    'S2': 'Selecione S2',
    'Core': 'Selecione o Núcleo',
    'Cable': 'Selecione o Cabo',
    'Primary Cable': 'Selecione o Cabo do Primário',
    'Secondary Cable': 'Selecione o Cabo do Secundário'
}


# with open('GUI/texts-pt_BR.json', 'w') as json_file:
#     data = []
#     data.append(select_single_component_label)
#     data.append(select_multi_component_label)
#     json.dump(data, json_file, ensure_ascii=False, indent=4)


class SingleComponentSelector(Ui_SingleComponentSelectWindow):
    def __init__(self, available_components, language=ENGLISH):
        super(SingleComponentSelector, self).__init__()
        self.language = language
        self.viewport = QMainWindow()
        self.setupUi(self.viewport)

        self.select_button.clicked.connect(self.add_component)
        self.remove_button.clicked.connect(self.remove_component)

        self.selected_item = None
        self.component_being_selected = None
        self.model_available = None
        self.model_selected = None

        self.available_components = available_components

        self.selected_components = {}
        for componentType in self.available_components:
            self.selected_components[componentType] = []

        self.configuration_complete = False

    def open_window(self, component_being_selected):
        self.selected_item = None
        self.component_being_selected = component_being_selected
        self.label.setText(select_single_component_label[component_being_selected])

        self.model_available = QStandardItemModel(self.list_available)
        for name in self.available_components[component_being_selected]:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model_available.appendRow(item)
        self.list_available.setModel(self.model_available)
        try:
            self.list_available.clicked.connect(self.component_available_clicked)
        finally:
            self.model_selected = QStandardItemModel(self.list_selected)
            for name in self.selected_components[component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.list_selected.setModel(self.model_selected)
            try:
                self.list_selected.clicked.connect(self.component_selected_clicked)
            finally:
                self.viewport.show()

    def add_component(self):
        if self.selected_item is not None and len(
                self.selected_components[self.component_being_selected]) == 0 and self.selected_item.text() in \
                self.available_components[self.component_being_selected]:
            self.available_components[self.component_being_selected].remove(self.selected_item.text())
            self.selected_components[self.component_being_selected].append(self.selected_item.text())
            self.model_available = QStandardItemModel(self.list_available)
            for name in self.available_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_available.appendRow(item)
            self.list_available.setModel(self.model_available)

            self.model_selected = QStandardItemModel(self.list_selected)
            for name in self.selected_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.list_selected.setModel(self.model_selected)
            self.list_selected.clicked.connect(self.component_selected_clicked)
            self.selected_item = None

            self.configuration_complete = True
            for componentType in self.selected_components:
                if len(self.selected_components[componentType]) == 0:
                    self.configuration_complete = False
                    break

    def remove_component(self):
        if self.selected_item is not None and self.selected_item.text() in self.selected_components[
            self.component_being_selected]:
            self.available_components[self.component_being_selected].append(self.selected_item.text())
            self.selected_components[self.component_being_selected].remove(self.selected_item.text())
            self.model_available = QStandardItemModel(self.list_available)
            for name in self.available_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_available.appendRow(item)
            self.list_available.setModel(self.model_available)

            self.model_selected = QStandardItemModel(self.list_selected)
            for name in self.selected_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.list_selected.setModel(self.model_selected)
            self.selected_item = None

    def component_available_clicked(self, index):
        self.selected_item = self.model_available.itemFromIndex(index)

    def component_selected_clicked(self, index):
        self.selected_item = self.model_selected.itemFromIndex(index)

    def get_selected_components(self):
        return self.selected_components


class MultiComponentSelector(Ui_ComponentSelectWindow):
    def __init__(self, available_components, parent=None):
        super(MultiComponentSelector, self).__init__()
        self.parent = parent
        self.viewport = QMainWindow()
        self.setupUi(self.viewport)

        self.add_button.clicked.connect(self.add_component)
        self.remove_button.clicked.connect(self.remove_component)

        self.selected_item = None
        self.component_being_selected = None
        self.model_available = None
        self.model_selected = None

        self.available_components = available_components

        self.selected_components = {}
        for componentType in self.available_components:
            self.selected_components[componentType] = []

        self.configuration_complete = False

    def open_window(self, component_being_selected):
        self.selected_item = None
        self.component_being_selected = component_being_selected
        self.label.setText(select_multi_component_label[component_being_selected])

        self.model_available = QStandardItemModel(self.list_available)
        for name in self.available_components[component_being_selected]:
            item = QStandardItem(name)
            item.setEditable(False)
            self.model_available.appendRow(item)
        self.list_available.setModel(self.model_available)
        try:
            self.list_available.clicked.connect(self.component_available_clicked)
        finally:
            self.model_selected = QStandardItemModel(self.list_selected)
            for name in self.selected_components[component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.list_selected.setModel(self.model_selected)
            try:
                self.list_selected.clicked.connect(self.component_selected_clicked)
            finally:
                self.viewport.show()

    def add_component(self):
        if self.selected_item is not None and self.selected_item.text() in self.available_components[
            self.component_being_selected]:
            self.available_components[self.component_being_selected].remove(self.selected_item.text())
            self.selected_components[self.component_being_selected].append(self.selected_item.text())
            self.model_available = QStandardItemModel(self.list_available)
            for name in self.available_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_available.appendRow(item)
            self.list_available.setModel(self.model_available)

            self.model_selected = QStandardItemModel(self.list_selected)
            for name in self.selected_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.list_selected.setModel(self.model_selected)
            self.list_selected.clicked.connect(self.component_selected_clicked)
            self.selected_item = None

            self.configuration_complete = True
            for componentType in self.selected_components:
                if len(self.selected_components[componentType]) == 0:
                    self.configuration_complete = False
                    break

    def remove_component(self):
        if self.selected_item is not None and self.selected_item.text() in self.selected_components[
            self.component_being_selected]:
            self.available_components[self.component_being_selected].append(self.selected_item.text())
            self.selected_components[self.component_being_selected].remove(self.selected_item.text())
            self.model_available = QStandardItemModel(self.list_available)
            for name in self.available_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_available.appendRow(item)
            self.list_available.setModel(self.model_available)

            self.model_selected = QStandardItemModel(self.list_selected)
            for name in self.selected_components[self.component_being_selected]:
                item = QStandardItem(name)
                item.setEditable(False)
                self.model_selected.appendRow(item)
            self.list_selected.setModel(self.model_selected)
            self.selected_item = None

    def component_available_clicked(self, index):
        self.selected_item = self.model_available.itemFromIndex(index)

    def component_selected_clicked(self, index):
        self.selected_item = self.model_selected.itemFromIndex(index)

    def get_selected_components(self):
        return self.selected_components
