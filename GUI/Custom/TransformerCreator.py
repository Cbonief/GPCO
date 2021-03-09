from functools import partial

from PyQt5.QtWidgets import *
from numpy import prod

from Converter.Components import Transformer
from GUI.Custom.ComponentSelector import SingleComponentSelector
from GUI.Custom.transformerCreateWindow import Ui_CreateTransformerWindow

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
        if prod(self.N > [0, 0], dtype=bool) > 0 and prod(self.Ncond > [0, 0],
                                                          dtype=bool) and self.component_selector.all_configured():
            components = self.component_selector.get_selected_components()
            database = self.parent.components.database
            ku = self.parent.security_configuration.get_parameters()['ku Transformer']
            core = database['Cores'][components['Core']]
            cables = [database['Cables'][components['Primary Cable']],
                      database['Cables'][components['Secondary Cable']]]
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

    def verify(self):
        if not (prod(self.N > [0, 0], dtype=bool) > 0 and prod(self.Ncond > [0, 0],
                                                               dtype=bool) and self.component_selector.all_configured()):
            self.finished = False
        else:
            components = self.component_selector.get_selected_components()
            database = self.parent.components.database
            ku = self.parent.security_configuration.get_parameters()['ku Transformer']
            core = database['Cores'][components['Core']]
            cables = [database['Cables'][components['Primary Cable']],
                      database['Cables'][components['Secondary Cable']]]
            new_transformer = Transformer(core, cables, self.N, self.Ncond, 'Transformador')
            self.finished = new_transformer.is_feasible(ku)
            if self.finished:
                self.transformer = new_transformer

    def get_transformer(self):
        return self.transformer

    def is_configured(self):
        return self.finished

    def set_parameters(self, params):
        if params is not None:
            self.N[PRIMARY] = params['Primary N']
            self.Ncond[PRIMARY] = params['Primary Ncond']
            self.N[SECONDARY] = params['Secondary N']
            self.Ncond[SECONDARY] = params['Secondary Ncond']
            self.component_selector.set_selected_components(
                {
                    'Core': params['Core'],
                    'Primary Cable': params['Primary Cable'],
                    'Secondary Cable': params['Secondary Cable']
                }
            )
            self.verify()

    def reset(self):
        self.N[PRIMARY] = 0
        self.Ncond[PRIMARY] = 0
        self.N[SECONDARY] = 0
        self.Ncond[SECONDARY] = 0
        self.component_selector.set_selected_components(
            {
                'Core': None,
                'Primary Cable': None,
                'Secondary Cable': None
            }
        )
