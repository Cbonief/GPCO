from functools import partial

from GUI.Handlers.ComponentSelector import SingleComponentSelector
from GUI.Handlers.inductorCreateWindow import Ui_CreateInductorWindow
from PyQt5.QtWidgets import *
from Converter.Components import Inductor

ComponentsSelectedPT3 = {
    'Li': 'Indutor de Entrada',
    'Lk': 'Indutor Auxiliar'
}

ENGLISH = 0
PORTUGUESE = 1


class InductorCreationHandler(Ui_CreateInductorWindow):
    def __init__(self, available_components, language=ENGLISH, parent=None):
        super(InductorCreationHandler, self).__init__()
        self.parent = parent
        self.language = language
        self.viewport = QMainWindow()
        self.setupUi(self.viewport)
        self.inductor_being_created = None
        self.pushButtonVerify.clicked.connect(self.verify_inductor)
        self.pushButtonCoreSel.clicked.connect(partial(self.open_selection, 'Core'))
        self.pushButtonCableSel.clicked.connect(partial(self.open_selection, 'Cable'))
        self.spinbox_N.valueChanged.connect(self.set_N)
        self.spinbox_Np.valueChanged.connect(self.set_Ncond)
        self.component_selector = {inductor: SingleComponentSelector(available_components[inductor]) for inductor in available_components}

        self.inductors = {}
        self.N = {}
        self.Ncond = {}
        self.finished = {}
        for inductor in available_components:
            self.N[inductor] = 0
            self.Ncond[inductor] = 0
            self.finished[inductor] = False

    def open_window(self, inductor_name):
        self.inductor_being_created = inductor_name
        self.viewport.setWindowTitle(ComponentsSelectedPT3[inductor_name])
        self.spinbox_N.setValue(self.N[inductor_name])
        self.spinbox_Np.setValue(self.Ncond[inductor_name])
        self.viewport.show()

    def set_N(self):
        self.N[self.inductor_being_created] = self.spinbox_N.value()

    def set_Ncond(self):
        self.Ncond[self.inductor_being_created] = self.spinbox_Np.value()

    def open_selection(self, component):
        self.component_selector[self.inductor_being_created].open_window(component)

    def verify_inductor(self):
        Ncond = self.spinbox_Np.value()
        N = self.spinbox_N.value()
        map = {
            'Li': 'EntranceInductor',
            'Lk': 'AuxiliaryInductor'
        }
        if N > 0 and Ncond > 0 and self.component_selector[self.inductor_being_created].configuration_complete:
            components = self.component_selector[self.inductor_being_created].get_selected_components()
            database = self.parent.components_database
            ku = self.parent.safety_params['ku'][map[self.inductor_being_created]]
            core = database['Cores'][components['Core'][0]]
            cable = database['Cables'][components['Cable'][0]]
            new_inductor = Inductor(core, cable, N, Ncond, self.inductor_being_created)
            if new_inductor.is_feasible(ku):
                message = QMessageBox()
                message.setWindowTitle("FIM")
                message.setText("Indutor Salvo.")
                message.setIcon(QMessageBox.Information)
                message.exec_()
                self.inductors[self.inductor_being_created] = new_inductor
                self.finished[self.inductor_being_created] = True
            else:
                warning = QMessageBox()
                warning.setWindowTitle("FIM")
                warning.setText("O Indutor Construído é Inválido e não Será Salvo")
                warning.setInformativeText("O Fator de Utilização é de {}%".format(round(100*new_inductor.utilization_factor(ku))))
                warning.setIcon(QMessageBox.Warning)

                warning.exec_()
        else:
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO")
            warning.setText("Algum Parâmetro do Indutor não foi configurado.")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()

    def get_Li(self):
        return self.inductors['Li']

    def get_Lk(self):
        return self.inductors['Lk']