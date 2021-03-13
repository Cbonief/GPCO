import datetime
import json
import sys
from functools import partial
import numpy as np

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QStyleFactory

from GUI.MainWindow import MainWindow

from GUI.Custom.ComponentSelector import SingleComponentSelector, MultiComponentSelector
from GUI.Custom.FeatureExtractor import FeatureExtractor
from GUI.Custom.FileHandler import ComponentsReader
from GUI.Custom.InductorCreator import InductorCreationHandler
from GUI.Custom.OptimizerConfigurationWindow import OptimizerConfigurationWindow
from GUI.Custom.PopUpWindow import warning, selection_pop_up
from GUI.Custom.SecurityConfigurationWindow import SecurityConfigurationWindow
from GUI.Custom.ThreadsHandler import Worker
from GUI.Custom.TransformerCreator import TransformerCreationHandler
from GUI.Custom.Widgets import CenteredWidget, SpacedWidget
from Optimizer.CustomUtilization import threaded_continuous_optimization, threaded_complete_optimization



class OptimizationMode:
    COMPLETE = 0
    CONTINUOUS_ONLY = 1



class Application(MainWindow):
    def __init__(self):
        # Builds the GUI calling the MainWindow's constructor.
        super(Application, self).__init__()

        # Creates all input extraction handlers.
        additional_design_features = {'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15}, 'dVc1': 0.10, 'dVc2': 0.10}
        self.circuit_features_handler = FeatureExtractor(self.design_features_inputs, additional_design_features)

        
        # Creates an instance of the ComponentsReader class, which reads the entire component database on the
        # constructor.
        self.components = ComponentsReader()

        available_components, available_components_specific = self.components.create_available_components_maps()
        available_components_specific_no_mag = {}
        available_components_inductor = {}
        for component in available_components_specific:
            if component not in ['Li', 'Lk']:
                if component is not 'Transformer':
                    available_components_specific_no_mag[component] = available_components_specific[component]
            else:
                available_components_inductor[component] = available_components_specific[component]


        # Creates all component selectors, and magnetic component creation handler.
        self.single_component_selector = SingleComponentSelector(available_components_specific_no_mag)
        self.multi_component_selector = MultiComponentSelector(available_components)
        self.inductor_creator = InductorCreationHandler(available_components_inductor, parent=self)
        self.transformer_creator = TransformerCreationHandler(available_components_specific['Transformer'], parent=self)

        self.security_configuration = SecurityConfigurationWindow()
        self.optimizer_configuration = OptimizerConfigurationWindow()

        # Sets the default optimization mode to COMPLETE.
        self.optimization_mode = OptimizationMode.COMPLETE

        # Configures the default save file name.
        aux = "config{:%m%d%Y}"
        self.default_file_name = aux.format(datetime.datetime.today())
        self.current_save_file_name = self.default_file_name
        self.number_of_files_created = 0

        # Indicates that a new file was created. Used to identify when the save file dialog should pop up.
        self.new_file_was_created = True

        # Thread Pool for running the Optimizer
        self.thread_pool = QThreadPool()
        self.is_running_optimizer = False       # Stops the optimizer from running more than once.

        # Loads the test file.
        self.load_data_from_file("test_file.json")
        

        # Connects all actions.
        self.connect_actions()

    # Connects all buttons and menu bar actions to their respective function.
    def connect_actions(self):
        self.select_components_tab.currentChanged.connect(self.set_optimization_mode)

        for button in self.complete_component_selection_buttons.items():
            button[1].clicked.connect(partial(self.multi_component_selector.open_window, button[0]))

        for button in self.continuous_component_selection_buttons.items():
            if button[0] not in ['Li', 'Lk', 'Tr']:
                button[1].clicked.connect(partial(self.single_component_selector.open_window, button[0]))

        self.continuous_component_selection_buttons['Li'].clicked.connect(partial(self.inductor_creator.open_window, 'Li'))
        self.continuous_component_selection_buttons['Lk'].clicked.connect(partial(self.inductor_creator.open_window, 'Lk'))
        self.continuous_component_selection_buttons['Tr'].clicked.connect(self.transformer_creator.open_window)

        self.actionNew.triggered.connect(self.create_file)
        self.actionSave.triggered.connect(self.save_file)
        self.actionSaveAs.triggered.connect(self.save_file_as)
        self.actionOpen.triggered.connect(self.open_file)
        self.actionConfigSecurity.triggered.connect(self.security_configuration.open_window)
        self.actionConfigOptimizer.triggered.connect(self.optimizer_configuration.open_window)
        self.action_run_optimizer.triggered.connect(self.run_optimizer)
        self.action_stop_optimizer.triggered.connect(self.stop_optimizer)

    # Automatically sets the Optimization Mode based on the selected tab.
    def set_optimization_mode(self):
        self.optimization_mode = self.select_components_tab.currentIndex()

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

    # Opens a configuration file and loads it's content.
    def open_file(self):
        filename, other = QFileDialog.getOpenFileName(self, "Open File", filter='*.json')
        self.load_data_from_file(filename)

    # Loads all the JSON content and sets all the configurations on the handlers, and UI.
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
                self.select_components_tab.setCurrentIndex(self.optimization_mode)
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
        if not self.is_running_optimizer:
            print("Started Optimizer")
            a = self.circuit_features_handler.is_ready()
            b = self.security_configuration.is_configured()
            c = False
            if self.optimization_mode == OptimizationMode.COMPLETE:
                c = self.multi_component_selector.all_configured()
            elif self.optimization_mode == OptimizationMode.CONTINUOUS_ONLY:
                c = self.single_component_selector.all_configured() and self.inductor_creator.all_configured() and self.transformer_creator.is_configured()

            if a and b and c:
                design_features = self.circuit_features_handler.get_features()
                design_features['dIin_max'] = design_features['dIin_max'] / 100
                design_features['dVo_max'] = design_features['dVo_max'] / 100
                safety_parameters = self.security_configuration.get_parameters()
                safety_parameters['Jmax'] = safety_parameters['Jmax'] * 1e4
                num_opt_config = self.optimizer_configuration.get_opt_config()
                components_data_base = self.components.database
                if self.optimization_mode == OptimizationMode.COMPLETE:
                    selected_components_keys = self.multi_component_selector.get_selected_components()
                    ga_config = self.optimizer_configuration.get_ga_config()

                    # Creates the worker thread for the Complete Optimizer.
                    worker = Worker(
                        threaded_complete_optimization,
                        selected_components_keys,
                        components_data_base,
                        design_features,
                        safety_parameters,
                        ga_config,
                        num_opt_config
                    )
                    worker.signals.result.connect(self.save_genetic_optimizer_result)
                    worker.signals.finished.connect(self.genetic_optimizer_finished_handler)
                    worker.signals.progress.connect(self.genetic_optimizer_progress_handler)

                    # Execute
                    self.thread_pool.start(worker)

                elif self.optimization_mode == OptimizationMode.CONTINUOUS_ONLY:
                    selected_components_keys = self.single_component_selector.get_selected_components()

                    # Creates the worker thread for the Continuous Optimizer.
                    worker = Worker(
                        threaded_continuous_optimization,
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
                self.is_running_optimizer = True
            else:
                warning("Conversor não configurado")

    def save_continuous_optimizer_result(self, result):
        best_loss, success, operation_point, converter = result
        self.converter_result_edit.setText(
            "Optimização Completa"
            "\nMelhores Perdas = {:.3e} W"
            "\nFrequência = {:.3e} Hz"
            "\nIndutância de Entrada = {:.3e} H"
            "\nIndutância Auxiliar = {:.3e} H"
            "\nConversor \n {}".format(best_loss, operation_point[0], operation_point[1], operation_point[2], converter)
        )
        frequency = np.logspace(3, 5, 100)
        Li = operation_point[1]
        Lk = operation_point[2]
        loss_vec = np.zeros(100)
        for i in range(0, 100):
            loss_vec[i] = converter.compensated_total_loss([frequency[i], Li, Lk])
            print(loss_vec[i], [frequency[i], Li, Lk])
        pen = mkPen(color=(255, 0, 0))
        self.optimizer_graph.plot(frequency, loss_vec, pen=pen)
        self.optimizer_graph.setTitle("Perdas x Frequência", color=(0, 0, 0), size='12pt')
        self.optimizer_graph.setLabel('left', 'Perdas (W)', **{'color':'#000'})
        self.optimizer_graph.setLabel('bottom', 'Frequência (Hz)', **{'color':'#000'})
        self.optimizer_graph.showGrid(x=True, y=True)
        self.optimizer_graph.setLogMode(x=True, y=False)

    def continuous_optimizer_progress_handler(self, percentage):
        self.optimization_progress_bar.setValue(percentage)

    def continuous_optimizer_finished_handler(self):
        self.optimization_progress_bar.reset()
        self.status_bar_text_edit.setText("Otimização Finalizada")
        self.is_running_optimizer = False

    def stop_optimizer(self):
        print("Stop")

    def save_genetic_optimizer_result(self, result):
        print(result)

    def get_data_from_string(self, data):
        aux = str(data)
        result = int(aux[2:7])/(10**(int(aux[1])))
        return result

    def genetic_optimizer_progress_handler(self, data):
        aux_string = str(data)
        data_case = int(aux_string[0])
        data_value = self.get_data_from_string(aux_string)
        print("Got {}th data = {}".format(data_case, self.get_data_from_string(aux_string)))
        if data_case == 3:
            self.optimization_progress_bar.setValue(int(data_value))

    def genetic_optimizer_finished_handler(self):
        print("AE CARAI")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = Application()
    form.show()
    form.update()  # start with something
    app.exec_()
    print("DONE")
