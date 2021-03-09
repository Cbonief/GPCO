import datetime
import json
import sys
from functools import partial

from PyQt5.QtCore import QSize, Qt, QCoreApplication, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget

from GUI.Custom.ComponentSelector import SingleComponentSelector, MultiComponentSelector
from GUI.Custom.FeatureExtractor import FeatureExtractor, LabeledInput
from GUI.Custom.FileHandler import ComponentsReader
from GUI.Custom.InductorCreator import InductorCreationHandler
from GUI.Custom.OptimizerConfigurationWindow import OptimizerConfigurationWindow
from GUI.Custom.PopUpWindow import warning, selection_pop_up
from GUI.Custom.SecurityConfigurationWindow import SecurityConfigurationWindow
from GUI.Custom.ThreadsHandler import Worker
from GUI.Custom.TransformerCreator import TransformerCreationHandler
from GUI.Custom.Widgets import CenteredWidget, SpacedWidget
from Optimizer.CustomUtilization import threaded_complete_optimization, \
    threaded_continuous_optimization

CONTINUOUS = ['C1', 'C2', 'C3', 'C4', 'D3', 'D4', 'S1', 'S2', 'Li', 'Lk', 'Tr']
COMPLETE = ['Capacitors', 'Switches', 'Diodes', 'Cores', 'Cables']
CONVERTER_PARAMS = ['']


class OptimizationMode:
    COMPLETE = 0
    CONTINUOUS_ONLY = 1


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1080, 600)
        self.setMinimumSize(QSize(1080, 600))
        self.setMaximumSize(QSize(1366, 745))
        self.setWindowTitle("GPCO - General Power Converter Optimizer")

        main_widget = QWidget()
        self.component_selection_buttons = {}

        main_layout = QHBoxLayout()
        main_splitter = QSplitter(Qt.Horizontal, self)
        left_frame = QFrame(main_splitter)
        left_frame.setFrameShape(QFrame.Box)
        left_frame.setMaximumWidth(250)
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

        print("Oi")
        top_right_layout = QHBoxLayout()
        self.converter_result_edit = QTextBrowser()
        aux_frame = QFrame()
        aux_frame.setMaximumWidth(450)
        aux_layout = QHBoxLayout()
        optimizer_graph = PlotWidget()
        aux_layout.addWidget(optimizer_graph)
        aux_frame.setLayout(aux_layout)
        top_right_layout.addWidget(self.converter_result_edit)
        top_right_layout.addWidget(aux_frame)

        bottom_right_layout = QHBoxLayout()
        analysis_graph_1 = QTextBrowser()
        analysis_graph_2 = PlotWidget()
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

        design_features_inputs = {
            'Vi': LabeledInput('Tensão de Entrada (V)'),
            'Vo': LabeledInput('Tensão de Saída (V)'),
            'Po': LabeledInput('Potência de Saída (W)'),
            'dIin_max': LabeledInput('DeltaIinMax (%)'),
            'dVo_max': LabeledInput('DeltaVoMax (%)'),
        }
        for key in design_features_inputs:
            converter_config_layout.addLayout(design_features_inputs[key])

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
        self.optimization_progress_bar.setMaximumWidth(180)
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
        self.actionSwitch.setText(_translate("MainWindow", "Switch"))
        self.actionDiode.setText(_translate("MainWindow", "Diode"))
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

        # Creates all input extraction handlers.
        self.circuit_features_handler = FeatureExtractor(design_features_inputs,
                                                         {
                                                             'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3,
                                                                      'AuxiliaryInductor': 0.15}, 'dVc1': 0.10,
                                                             'dVc2': 0.10
                                                         }
                                                         )

        self.components = ComponentsReader()

        # Loads all components
        available_components, available_components_specific = self.components.create_available_components_maps()
        available_components_specific_no_mag = {}
        for component in available_components_specific:
            if component not in ['Li', 'Lk', 'Transformer']:
                available_components_specific_no_mag[component] = available_components_specific[component]
        self.single_component_selector = SingleComponentSelector(available_components_specific_no_mag)
        self.multi_component_selector = MultiComponentSelector(available_components)
        inductors = ['Li', 'Lk']
        available_components_inductor = {component: available_components_specific[component] for component in inductors}
        self.inductor_creator = InductorCreationHandler(available_components_inductor, parent=self)
        self.transformer_creator = TransformerCreationHandler(available_components_specific['Transformer'], parent=self)

        self.security_configuration = SecurityConfigurationWindow()
        self.optimizer_configuration = OptimizerConfigurationWindow()

        self.optimization_mode = OptimizationMode.COMPLETE

        aux = "config{:%m%d%Y}"
        self.default_file_name = aux.format(datetime.datetime.today())
        self.current_save_file_name = self.default_file_name
        self.number_of_files_created = 0
        self.new_file_was_created = True

        # Thread Pool for running the Optimizer
        self.thread_pool = QThreadPool()
        self.is_running_optimizer = False

        self.load_data_from_file("test_file.json")
        self.progress = 0

        # Connects all actions.
        self.connect_actions()

    def connect_actions(self):
        # self.optimize_button.clicked.connect(self.optimize)

        self.select_components_tab.currentChanged.connect(self.set_optimization_mode)

        for button in self.complete_component_selection_buttons.items():
            button[1].clicked.connect(partial(self.multi_component_selector.open_window, button[0]))

        for button in self.continuous_component_selection_buttons.items():
            if button[0] not in ['Li', 'Lk', 'Tr']:
                button[1].clicked.connect(partial(self.single_component_selector.open_window, button[0]))

        self.continuous_component_selection_buttons['Li'].clicked.connect(
            partial(self.inductor_creator.open_window, 'Li'))
        self.continuous_component_selection_buttons['Lk'].clicked.connect(
            partial(self.inductor_creator.open_window, 'Lk'))
        self.continuous_component_selection_buttons['Tr'].clicked.connect(self.transformer_creator.open_window)

        self.actionNew.triggered.connect(self.create_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionSaveAs.triggered.connect(self.save_file_as)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionConfigSecurity.triggered.connect(self.security_configuration.open_window)
        self.actionConfigOptimizer.triggered.connect(self.optimizer_configuration.open_window)
        self.action_run_optimizer.triggered.connect(self.run_optimizer)
        self.action_stop_optimizer.triggered.connect(self.stop_optimizer)

    def set_optimization_mode(self):
        self.optimization_mode = self.select_components_tab.currentIndex()

    ## TODO: Implement File IO.
    def create_file(self):
        print("Create File")
        selection_pop_up("Continuar", "Salvar Arquivo antes de Continuar?", self.create_file_handler)

    def create_file_handler(self, action):
        if action != -1:
            if action == 1:
                self.save_file()
            self.circuit_features_handler.reset_values()
            self.security_configuration.reset_values()
            self.optimizer_configuration.reset_values()
            self.multi_component_selector.reset()
            self.single_component_selector.reset()
            self.new_file_was_created = True
            self.number_of_files_created += 1
            self.default_file_name = self.default_file_name[:-1] + str(self.number_of_files_created)

    def save_file(self):
        if self.new_file_was_created:
            filename, other = QFileDialog.getSaveFileName(self, "Salvar Arquivo", self.default_file_name + '.json',
                                                          filter='*.json')
            if filename:
                with open(filename, 'w') as write_file:
                    json.dump(self.get_configurations_as_json(), write_file, indent=2)
                self.new_file_was_created = False
                self.current_save_file_name = filename
        else:
            with open(self.current_save_file_name, 'w') as write_file:
                json.dump(self.get_configurations_as_json(), write_file, indent=2)
                self.new_file_was_created = False

    def save_file_as(self):
        filename, other = QFileDialog.getSaveFileName(self, "Salvar Arquivo", self.default_file_name + '.json',
                                                      filter='*.json')
        if filename:
            with open(filename, 'w') as write_file:
                json.dump(self.get_configurations_as_json(), write_file, indent=2)
            self.current_save_file_name = filename

    def get_configurations_as_json(self):
        saved_data = [
            self.multi_component_selector.get_selected_components(),
            self.single_component_selector.get_selected_components(),
            self.security_configuration.get_parameters(),
            self.optimizer_configuration.get_features(),
            self.circuit_features_handler.get_features(),
            self.optimization_mode
        ]
        if self.inductor_creator.finished['Li']:
            saved_data.append(self.inductor_creator.get_Li().get_dictionary())
        else:
            saved_data.append(None)
        if self.inductor_creator.finished['Lk']:
            saved_data.append(self.inductor_creator.get_Lk().get_dictionary())
        else:
            saved_data.append(None)
        if self.transformer_creator.is_configured():
            saved_data.append(self.transformer_creator.get_transformer().get_dictionary())
        else:
            saved_data.append(None)
        return saved_data

    # Reads configurations from a JSon File.
    def open_file(self):
        filename, other = QFileDialog.getOpenFileName(self, "Open File", filter='*.json')
        self.load_data_from_file(filename)

    def load_data_from_file(self, filename):
        if filename:
            with open(filename, "r") as read_file:
                data = json.load(read_file)
                self.multi_component_selector.set_selected_components(data[0])
                self.single_component_selector.set_selected_components(data[1])
                self.security_configuration.set_parameters(data[2])
                self.optimizer_configuration.set_features(data[3])
                self.circuit_features_handler.set_features(data[4])
                self.optimization_mode = data[5]
                Li_dictionary = data[6]
                Lk_dictionary = data[7]
                Transfromer_dictionary = data[8]
                self.inductor_creator.reset()
                self.transformer_creator.reset()
                self.inductor_creator.set_parameters(Li_dictionary, Lk_dictionary)
                self.transformer_creator.set_parameters(Transfromer_dictionary)
            self.current_save_file_name = filename
            self.new_file_was_created = False

    def run_optimizer(self):
        a = self.circuit_features_handler.is_ready()
        b = self.security_configuration.is_configured()
        c = False
        if self.optimization_mode == OptimizationMode.COMPLETE:
            c = self.multi_component_selector.all_configured()
        elif self.optimization_mode == OptimizationMode.CONTINUOUS_ONLY:
            c = self.single_component_selector.all_configured() and self.inductor_creator.all_configured() and self.transformer_creator.is_configured()

        if a and b and c:
            # Is ready to start the optimization.
            design_features = self.circuit_features_handler.get_features()
            design_features['dIin_max'] = design_features['dIin_max'] / 100
            design_features['dVo_max'] = design_features['dVo_max'] / 100
            safety_parameters = self.security_configuration.get_parameters()
            safety_parameters['Jmax'] = safety_parameters['Jmax'] * 1e4
            print(self.security_configuration.get_parameters())
            num_opt_config = self.optimizer_configuration.get_opt_config()
            components_data_base = self.components.database
            if self.optimization_mode == OptimizationMode.COMPLETE:
                selected_components_keys = self.multi_component_selector.get_selected_components()
                ga_config = self.optimizer_configuration.get_ga_config()

                # Pass the function to execute
                worker = Worker(threaded_complete_optimization,
                                selected_components_keys,
                                components_data_base,
                                design_features,
                                safety_parameters,
                                ga_config,
                                num_opt_config
                                )
                worker.signals.result.connect(self.print_output)
                worker.signals.finished.connect(self.thread_complete)

                # Execute
                self.thread_pool.start(worker)
            elif self.optimization_mode == OptimizationMode.CONTINUOUS_ONLY:
                selected_components_keys = self.single_component_selector.get_selected_components()
                worker = Worker(threaded_continuous_optimization,
                                selected_components_keys,
                                components_data_base,
                                self.transformer_creator.transformer,
                                self.inductor_creator.inductors['Li'],
                                self.inductor_creator.inductors['Lk'],
                                design_features,
                                safety_parameters,
                                num_opt_config
                                )
                worker.signals.result.connect(self.save_continuous_optimizer_result)
                worker.signals.finished.connect(self.continuous_optimizer_finished_handler)
                worker.signals.progress.connect(self.continuous_optimizer_progress_handler)

                # Execute
                self.thread_pool.start(worker)

            self.status_bar_text_edit.setText("Otimização em Progresso")
        else:
            warning("Conversor não configurado")

    def save_continuous_optimizer_result(self, result):
        best_loss, success, operation_point, converter = result
        self.converter_result_edit.setText(
            "Optimização Completa"
            "\nFrequência = {:.3e} Hz"
            "\nIndutância de Entrada = {:.3e} H"
            "\nIndutância Auxiliar = {:.3e} H"
            "\nConversor \n {}".format(operation_point[0], operation_point[1], operation_point[2], converter)
        )

    def continuous_optimizer_progress_handler(self, percentage):
        self.optimization_progress_bar.setValue(percentage)

    def continuous_optimizer_finished_handler(self):
        self.progress = 0
        self.optimization_progress_bar.reset()
        self.status_bar_text_edit.setText("Otimização Finalizada")

    def stop_optimizer(self):
        self.progress += 1
        self.optimization_progress_bar.setValue(self.progress)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = Application()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
