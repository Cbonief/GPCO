from functools import partial

from PyQt5.QtWidgets import *

from Converter.Components import Inductor
from GUI.Custom.ComponentSelector import SingleComponentSelector
from GUI.Custom.inductorCreateWindow import Ui_CreateInductorWindow

ComponentsSelectedPT3 = {
    'Li': 'Indutor de Entrada',
    'Lk': 'Indutor Auxiliar'
}

ku_map = {
    'Li': 'ku EntranceInductor',
    'Lk': 'ku AuxiliaryInductor'
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
        self.pushButtonVerify.clicked.connect(self.verify_and_save_inductor)
        self.pushButtonCoreSel.clicked.connect(partial(self.open_selection, 'Core'))
        self.pushButtonCableSel.clicked.connect(partial(self.open_selection, 'Cable'))
        self.spinbox_N.valueChanged.connect(self.set_N)
        self.spinbox_Np.valueChanged.connect(self.set_Ncond)
        self.component_selector = {inductor: SingleComponentSelector(available_components[inductor]) for inductor in available_components}

        self.inductors = {'Li': None, 'Lk': None}
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

    def verify_and_save_inductor(self):
        Ncond = self.spinbox_Np.value()
        N = self.spinbox_N.value()
        if N > 0 and Ncond > 0 and self.component_selector[self.inductor_being_created].all_configured():
            components = self.component_selector[self.inductor_being_created].get_selected_components()
            database = self.parent.components.database
            ku = self.parent.security_configuration.get_parameters()[ku_map[self.inductor_being_created]]
            core = database['Cores'][components['Core']]
            cable = database['Cables'][components['Cable']]
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
                warning.setInformativeText(
                    "O Fator de Utilização é de {}%".format(round(100 * new_inductor.utilization_factor(ku))))
                warning.setIcon(QMessageBox.Warning)
                warning.exec_()
        else:
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO")
            warning.setText("Algum Parâmetro do Indutor não foi configurado.")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()

    def verify_inductor(self, inductor=None):
        if inductor is None:
            inductor = self.inductor_being_created
        N = self.N[inductor]
        Ncond = self.Ncond[inductor]
        if N <= 0 or Ncond <= 0 or not self.component_selector[inductor].all_configured():
            self.finished[inductor] = False
        else:
            components = self.component_selector[inductor].get_selected_components()
            database = self.parent.components.database
            ku = self.parent.security_configuration.get_parameters()[ku_map[inductor]]
            core = database['Cores'][components['Core']]
            cable = database['Cables'][components['Cable']]
            new_inductor = Inductor(core, cable, N, Ncond)
            self.finished[inductor] = new_inductor.is_feasible(ku)
            if self.finished[inductor]:
                self.inductors[inductor] = new_inductor

    def verify_all_inductors(self):
        for inductor in self.inductors.keys():
            self.verify_inductor(inductor)

    def get_Li(self):
        return self.inductors['Li']

    def get_Lk(self):
        return self.inductors['Lk']

    def all_configured(self):
        return self.finished['Li'] and self.finished['Lk']

    def set_parameters(self, params_Li, params_Lk):
        if params_Li is not None:
            self.N['Li'] = params_Li['N']
            self.Ncond['Li'] = params_Li['Ncond']
            self.component_selector['Li'].set_selected_components(
                {'Core': params_Li['Core'], 'Cable': params_Li['Cable']})
        if params_Lk is not None:
            self.N['Lk'] = params_Lk['N']
            self.Ncond['Lk'] = params_Lk['Ncond']
            self.component_selector['Lk'].set_selected_components(
                {'Core': params_Lk['Core'], 'Cable': params_Lk['Cable']})
        self.verify_all_inductors()

    def reset(self):
        self.N = {'Li': 0, 'Lk': 0}
        self.Ncond = {'Li': 0, 'Lk': 0}
        self.component_selector['Li'].reset()
        self.component_selector['Lk'].reset()
