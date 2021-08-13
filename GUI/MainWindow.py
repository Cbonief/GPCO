from PyQt5.QtCore import QSize, Qt, QCoreApplication, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, mkPen
from GUI.Custom.Widgets import CenteredWidget, SpacedWidget, LabeledInput

CONTINUOUS = ['C1', 'C2', 'C3', 'C4', 'D3', 'D4', 'S1', 'S2', 'Li', 'Lk', 'Tr']
COMPLETE = ['Capacitors', 'Switches', 'Diodes', 'Cores', 'Cables']


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1080, 600)
        self.setMinimumSize(QSize(1080, 600))
        self.setMaximumSize(QSize(1600, 900))
        self.setWindowTitle("GPCO - General Power Converter Optimizer")

        main_widget = QWidget()
        self.component_selection_buttons = {}

        main_layout = QHBoxLayout()
        main_splitter = QSplitter(Qt.Horizontal, self)
        left_frame = QFrame(main_splitter)
        left_frame.setFrameShape(QFrame.Box)
        left_frame.setMaximumWidth(300)
        left_frame.setMinimumWidth(220)
        right_frame = QFrame(main_splitter)
        right_frame.setFrameShape(QFrame.Box)
        main_splitter.addWidget(left_frame)
        main_splitter.addWidget(right_frame)

        converter_config_layout = QVBoxLayout()

        visualize_information_layout = QVBoxLayout()
        right_splitter = QSplitter(Qt.Vertical)
        visualize_information_layout.addWidget(right_splitter)
        top_right_frame = QFrame(right_splitter)
        bottom_right_frame = QFrame(right_splitter)
        right_splitter.addWidget(top_right_frame)
        right_splitter.addWidget(bottom_right_frame)

        top_right_layout = QHBoxLayout()
        self.converter_result_edit = QTextBrowser()
        self.optimizer_graph = PlotWidget()
        self.optimizer_graph.setBackground('w')
        aux_frame = QFrame()
        aux_frame.setMaximumWidth(450)
        aux_layout = QHBoxLayout()
        aux_layout.addWidget(self.optimizer_graph)
        aux_frame.setLayout(aux_layout)
        top_right_layout.addWidget(self.converter_result_edit)
        top_right_layout.addWidget(aux_frame)

        bottom_right_layout = QHBoxLayout()
        analysis_graph_1 = QTextBrowser()
        analysis_graph_2 = PlotWidget()
        analysis_graph_2.setBackground('w')
        aux_frame2 = QFrame()
        aux_frame2.setMaximumWidth(450)
        aux_layout2 = QHBoxLayout()
        aux_layout2.addWidget(analysis_graph_2)
        aux_frame2.setLayout(aux_layout2)
        bottom_right_layout.addWidget(analysis_graph_1)
        bottom_right_layout.addWidget(aux_frame2)

        top_right_frame.setLayout(top_right_layout)
        bottom_right_frame.setLayout(bottom_right_layout)

        # Adiciona tudo que vai no Layout do Conversor
        configuration_label = QLabel(
            "<html><head/><body><p><span style=\" font-size:12pt;\">Configuração do Conversor</span></p></body></html>"
        )
        configuration_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        configuration_label.setAlignment(Qt.AlignCenter)
        converter_config_layout.addWidget(configuration_label)
        topology_label = QLabel(
            "<html><head/><body><p><span style=\" font-size:10pt;\">Topologia</span></p></body></html>"
        )
        topology_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        topology_label.setAlignment(Qt.AlignCenter)
        converter_config_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Minimum))
        converter_config_layout.addWidget(topology_label)
        converter_config_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Minimum))
        converter_selector = QComboBox()
        converter_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        converter_selector.addItem("Boost Half Bridge")
        converter_config_layout.addLayout(CenteredWidget(converter_selector))
        parameters_label = QLabel(
            "<html><head/><body><p><span style=\" font-size:10pt;\">Parâmetros de Projeto</span></p></body></html>"
        )
        parameters_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        parameters_label.setAlignment(Qt.AlignCenter)
        converter_config_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        converter_config_layout.addWidget(parameters_label)
        converter_config_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.design_features_inputs = {
            'Vi': LabeledInput('Tensão de Entrada (V)', spacing=[10, 20]),
            'Vo': LabeledInput('Tensão de Saída (V)', spacing=[10, 20]),
            'Po': LabeledInput('Potência de Saída (W)', spacing=[10, 20]),
            'dIin_max': LabeledInput('DeltaIinMax (%)', spacing=[10, 20]),
            'dVo_max': LabeledInput('DeltaVoMax (%)', spacing=[10, 20]),
        }
        for key in self.design_features_inputs:
            converter_config_layout.addLayout(self.design_features_inputs[key])

        converter_config_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        select_components_label = QLabel(
            "<html><head/><body><p><span style=\" font-size:10pt;\">Selecione os Componentes</span></p></body></html>"
        )
        select_components_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        select_components_label.setAlignment(Qt.AlignCenter)
        converter_config_layout.addWidget(select_components_label)

        self.select_components_tab = QTabWidget()
        complete_optimization_components_tab = QFrame()
        continuous_optimization_components_tab = QFrame()
        complete_optimization_components_tab.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        continuous_optimization_components_tab.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        continuous_optimization_components_layout = QVBoxLayout()
        complete_optimization_components_layout = QVBoxLayout()

        self.complete_component_selection_buttons = {}
        self.continuous_component_selection_buttons = {}

        for component in COMPLETE:
            self.complete_component_selection_buttons[component] = QPushButton(component)
        for component in CONTINUOUS:
            self.continuous_component_selection_buttons[component] = QPushButton(component)

        complete_optimization_components_layout.addLayout(
            SpacedWidget([self.complete_component_selection_buttons['Capacitors']])
        )
        complete_optimization_components_layout.addLayout(
            SpacedWidget([self.complete_component_selection_buttons['Diodes'],
                          self.complete_component_selection_buttons['Switches']])
        )
        complete_optimization_components_layout.addLayout(
            SpacedWidget([self.complete_component_selection_buttons['Cores'],
                          self.complete_component_selection_buttons['Cables']])
        )
        complete_optimization_components_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        complete_optimization_components_tab.setLayout(complete_optimization_components_layout)

        continuous_optimization_components_layout.addLayout(
            SpacedWidget([self.continuous_component_selection_buttons['C1'],
                          self.continuous_component_selection_buttons['C2']])
        )
        continuous_optimization_components_layout.addLayout(
            SpacedWidget([self.continuous_component_selection_buttons['C3'],
                          self.continuous_component_selection_buttons['C4']])
        )
        continuous_optimization_components_layout.addLayout(
            SpacedWidget([self.continuous_component_selection_buttons['S1'],
                          self.continuous_component_selection_buttons['S2']])
        )
        continuous_optimization_components_layout.addLayout(
            SpacedWidget([self.continuous_component_selection_buttons['D3'],
                          self.continuous_component_selection_buttons['D4']])
        )
        continuous_optimization_components_layout.addLayout(
            SpacedWidget([self.continuous_component_selection_buttons['Li'],
                          self.continuous_component_selection_buttons['Lk']])
        )
        continuous_optimization_components_layout.addLayout(
            SpacedWidget([self.continuous_component_selection_buttons['Tr']])
        )
        continuous_optimization_components_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        continuous_optimization_components_tab.setLayout(continuous_optimization_components_layout)

        self.select_components_tab.addTab(complete_optimization_components_tab, "Completa")
        self.select_components_tab.addTab(continuous_optimization_components_tab, "Contínua")
        converter_config_layout.addWidget(self.select_components_tab)

        left_frame.setLayout(converter_config_layout)
        right_frame.setLayout(visualize_information_layout)
        main_layout.addWidget(main_splitter)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Create all action menus.
        self.menu_bar = QMenuBar(self)
        self.file_menu = QMenu(self.menu_bar)
        self.run_menu = QMenu(self.menu_bar)
        self.components_menu = QMenu(self.menu_bar)
        self.add_component_menu = QMenu(self.components_menu)
        self.settings_menu = QMenu(self.menu_bar)
        self.help_menu = QMenu(self.menu_bar)
        self.setMenuBar(self.menu_bar)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.optimization_progress_bar = QProgressBar(self)
        self.optimization_progress_bar.setMaximumWidth(250)
        self.status_bar_text_edit = QLabel("")
        self.status_bar.addPermanentWidget(self.optimization_progress_bar, 1)
        self.status_bar.addPermanentWidget(self.status_bar_text_edit, 1)

        self.actionNew = QAction(self)
        self.actionNew.setIcon(QIcon("GUI/Icons/document--add.svg"))
        self.actionOpen = QAction(self)
        self.actionOpen.setIcon(QIcon("GUI/Icons/folder.svg"))
        self.actionSave = QAction(self)
        self.actionSave.setIcon(QIcon("GUI/Icons/save.svg"))
        self.actionSaveAs = QAction(self)
        self.actionSaveAs.setIcon(QIcon("GUI/Icons/save.svg"))
        self.actionSwitch = QAction(self)
        self.actionDiode = QAction(self)
        self.actionCapacitor = QAction(self)
        self.actionCable = QAction(self)
        self.actionCore = QAction(self)
        self.actionConfigOptimizer = QAction(self)
        self.actionConfigSecurity = QAction(self)
        self.actionTransformer = QAction(self)
        self.actionInductor = QAction(self)
        self.actionHowItWorks = QAction(self)
        self.actionHowToUse = QAction(self)
        self.actionLoadFile = QAction(self)
        self.action_run_optimizer = QAction(self)
        self.action_run_optimizer.setIcon(QIcon("GUI/Icons/play--filled--alt.svg"))
        self.action_stop_optimizer = QAction(self)
        self.action_stop_optimizer.setIcon(QIcon("GUI/Icons/stop--filled--alt.svg"))
        self.actionComponents = QAction(self)
        self.file_menu.addAction(self.actionNew)
        self.file_menu.addAction(self.actionOpen)
        self.file_menu.addAction(self.actionSave)
        self.file_menu.addAction(self.actionSaveAs)
        self.add_component_menu.addAction(self.actionSwitch)
        self.add_component_menu.addAction(self.actionDiode)
        self.add_component_menu.addAction(self.actionCapacitor)
        self.add_component_menu.addAction(self.actionCable)
        self.add_component_menu.addAction(self.actionCore)
        self.add_component_menu.addAction(self.actionTransformer)
        self.add_component_menu.addAction(self.actionInductor)
        self.run_menu.addAction(self.action_run_optimizer)
        self.run_menu.addAction(self.action_stop_optimizer)
        self.components_menu.addAction(self.add_component_menu.menuAction())
        self.components_menu.addAction(self.actionLoadFile)
        self.settings_menu.addAction(self.actionConfigOptimizer)
        self.settings_menu.addAction(self.actionConfigSecurity)
        self.help_menu.addAction(self.actionHowItWorks)
        self.help_menu.addAction(self.actionHowToUse)
        self.menu_bar.addAction(self.file_menu.menuAction())
        self.menu_bar.addAction(self.run_menu.menuAction())
        self.menu_bar.addAction(self.components_menu.menuAction())
        self.menu_bar.addAction(self.settings_menu.menuAction())
        self.menu_bar.addAction(self.help_menu.menuAction())

        _translate = QCoreApplication.translate
        self.file_menu.setTitle(_translate("MainWindow", "Arquivo"))
        self.components_menu.setTitle(_translate("MainWindow", "Biblioteca"))
        self.help_menu.setTitle(_translate("MainWindow", "Ajuda"))
        self.settings_menu.setTitle(_translate("MainWindow", "Configurações"))
        self.run_menu.setTitle(_translate("MainWindow", "Rodar"))
        self.add_component_menu.setTitle(_translate("MainWindow", "Adicionar Componente"))
        self.actionNew.setText(_translate("MainWindow", "Novo Arquivo"))
        self.actionNew.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionOpen.setText(_translate("MainWindow", "Carregar Arquivo"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Salvar"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSaveAs.setText(_translate("MainWindow", "Salvar Como"))
        self.actionSaveAs.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionSwitch.setText(_translate("MainWindow", "Chave"))
        self.actionDiode.setText(_translate("MainWindow", "Diodo"))
        self.actionCapacitor.setText(_translate("MainWindow", "Capacitor"))
        self.actionCable.setText(_translate("MainWindow", "Fio"))
        self.actionCore.setText(_translate("MainWindow", "Núcleo Magnético"))
        self.actionConfigOptimizer.setText(_translate("MainWindow", "Otimizador"))
        self.actionConfigSecurity.setText(_translate("MainWindow", "Fatores de Segurança"))
        self.actionTransformer.setText(_translate("MainWindow", "Transformador"))
        self.actionInductor.setText(_translate("MainWindow", "Indutor"))
        self.actionHowItWorks.setText(_translate("MainWindow", "Como funciona o otimizador?"))
        self.actionHowToUse.setText(_translate("MainWindow", "Como utilizar o otimizador?"))
        self.actionLoadFile.setText(_translate("MainWindow", "Carregar Arquivo"))
        self.actionComponents.setText(_translate("MainWindow", "Componentes"))
        self.action_run_optimizer.setText(_translate("MainWindow", "Rodar Otimizador"))
        self.action_run_optimizer.setShortcut(_translate("MainWindow", "F5"))
        self.action_stop_optimizer.setText(_translate("MainWindow", "Parar Otimizador"))
        self.action_stop_optimizer.setShortcut(_translate("MainWindow", "F9"))

        # Execution Toolbar
        execution_toolbar = QToolBar("Run", self)
        execution_toolbar.addAction(self.actionNew)
        execution_toolbar.addAction(self.actionSave)
        execution_toolbar.addAction(self.actionOpen)
        execution_toolbar.addAction(self.action_run_optimizer)
        execution_toolbar.addAction(self.action_stop_optimizer)
        execution_toolbar.setFixedHeight(36)
        execution_toolbar.setIconSize(QSize(12, 12))
        self.addToolBar(execution_toolbar)
