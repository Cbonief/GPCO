from functools import partial

from GUI.Handlers.ComponentSelector import SingleComponentSelector
from GUI.Handlers.transformerCreateWindow import Ui_CreateTransformerWindow
from PyQt5.QtWidgets import *
from Converter.Components import Transformer
from numpy import prod

ENGLISH = 0
PORTUGUESE = 1

PRIMARY = 0
SECONDARY = 1


class TransformerCreationHandler(Ui_CreateTransformerWindow):
    def __init__(self, available_components, language=ENGLISH, parent=None):
        super(TransformerCreationHandler, self).__init__()
        self.parent = parent
        self.language = language
        self.viewport = QMainWindow()
        self.setupUi(self.viewport)
        self.buttonVerify.clicked.connect(self.verify_transformer)

        self.buttonCoreSel.clicked.connect(partial(self.open_selection, 'Core'))
        self.buttonPrimaryCableSel.clicked.connect(partial(self.open_selection, 'Primary Cable'))
        self.buttonSecondaryCableSel.clicked.connect(partial(self.open_selection, 'Secondary Cable'))

        self.input_Np.valueChanged.connect(self.set_Np)
        self.input_Npp.valueChanged.connect(self.set_NcondP)
        self.input_Ns.valueChanged.connect(self.set_Ns)
        self.input_Nps.valueChanged.connect(self.set_NcondS)

        self.component_selector = SingleComponentSelector(available_components)

        self.transformer = None
        self.N = [0, 0]
        self.Ncond = [0, 0]
        self.finished = False
        self.window_opened = False

    def open_window(self):
        self.viewport.setWindowTitle('Transformador')
        self.input_Np.setValue(self.N[PRIMARY])
        self.input_Npp.setValue(self.Ncond[PRIMARY])
        self.input_Ns.setValue(self.N[SECONDARY])
        self.input_Nps.setValue(self.Ncond[SECONDARY])
        self.window_opened = True
        self.viewport.show()

    def set_Np(self):
        self.N[PRIMARY] = self.input_Np.value()

    def set_NcondP(self):
        self.Ncond[PRIMARY] = self.input_Npp.value()

    def set_Ns(self):
        self.N[SECONDARY] = self.input_Ns.value()

    def set_NcondS(self):
        self.Ncond[SECONDARY] = self.input_Nps.value()

    def open_selection(self, component):
        self.component_selector.open_window(component)

    def verify_transformer(self):
        self.N[PRIMARY] = self.input_Np.value()
        self.Ncond[PRIMARY] = self.input_Npp.value()
        self.N[SECONDARY] = self.input_Ns.value()
        self.Ncond[SECONDARY] = self.input_Nps.value()
        if prod(self.N > [0, 0], dtype=bool) > 0 and prod(self.Ncond > [0, 0], dtype=bool) and self.component_selector.configuration_complete:
            components = self.component_selector.get_selected_components()
            database = self.parent.components_database
            ku = self.parent.safety_params['ku']['Transformer']
            core = database['Cores'][components['Core'][0]]
            cables = [database['Cables'][components['Primary Cable'][0]],  database['Cables'][components['Secondary Cable'][0]]]
            new_transformer = Transformer(core, cables, self.N, self.Ncond, 'Transformador')
            if new_transformer.is_feasible(ku):
                message = QMessageBox()
                message.setWindowTitle("FIM")
                message.setText("Transformador Salvo.")
                message.setIcon(QMessageBox.Information)
                message.exec_()
                self.transformer = new_transformer
                self.finished = True
            else:
                warning = QMessageBox()
                warning.setWindowTitle("FIM")
                warning.setText("O Transformador Construído é Inválido e não Será Salvo")
                warning.setInformativeText("O Fator de Utilização é de {}%".format(round(100*new_transformer.utilization_factor(ku))))
                warning.setIcon(QMessageBox.Warning)
                self.finished = False
                warning.exec_()
        else:
            warning = QMessageBox()
            warning.setWindowTitle("ATENÇÃO")
            warning.setText("Algum Parâmetro do Transformador não foi configurado.")
            warning.setIcon(QMessageBox.Warning)
            warning.exec_()
            self.finished = False

    def get_transformer(self):
        return self.transformer
