from pathlib import Path

from Converter.Components import *


def save_configurations():
    x = 2


class ComponentsReader:
    def __init__(self):
        self.database = {}
        self.load_components()

    # Done
    @staticmethod
    def load_core(filename):
        file = open(filename, "r")
        contents = file.readlines()
        file.close()
        param = {}
        core_name = None
        for line in contents:
            aux = line.split(": ")
            variable_name = aux[0]
            value = aux[1].split("\n")[0]
            if variable_name != "Name":
                param[variable_name] = float(value)
            else:
                core_name = value
        new_core = Core(param["AeAw"], param["Ae"], param["Aw"], param["Ve"], param["Alpha"], param["Beta"],
                        param["Kc"],
                        param["Lt"], 2, Name=core_name)
        return [new_core, core_name]

    def load_all_cores(self):
        cores = {}
        for file_path in Path("Saved Data/Components/Cores/").glob('**/*.txt'):
            [core, name] = self.load_core(str(file_path))
            cores[name] = core
        return cores

    @staticmethod
    def load_switch(filename):
        file = open(filename, "r")
        contents = file.readlines()
        file.close()
        param = {}
        component_name = None
        for line in contents:
            aux = line.split(": ")
            variable_name = aux[0]
            value = aux[1].split("\n")[0]
            if variable_name != "Name":
                param[variable_name] = float(value)
            else:
                component_name = value
        new_switch = Switch(param["Ton"], param["Toff"], param["Rd"], param['Vmax'], param['Cds'], Name=component_name)
        return [new_switch, component_name]

    def load_all_switches(self):
        switches = {}
        for file_path in Path("Saved Data/Components/Switches/").glob('**/*.txt'):
            [switch, name] = self.load_switch(str(file_path))
            switches[name] = switch
        return switches

    @staticmethod
    def load_capacitor(filename):
        file = open(filename, "r")
        contents = file.readlines()
        file.close()
        param = {}
        component_name = None
        for line in contents:
            aux = line.split(": ")
            variable_name = aux[0]
            value = aux[1].split("\n")[0]
            if variable_name != "Name":
                param[variable_name] = float(value)
            else:
                component_name = value
        new_capacitor = Capacitor(param["C"], param["Rse"], param['Vmax'], Name=component_name)
        return [new_capacitor, component_name]

    def load_all_capacitors(self):
        capacitors = {}
        for file_path in Path("Saved Data/Components/Capacitors/").glob('**/*.txt'):
            [capacitor, name] = self.load_capacitor(str(file_path))
            capacitors[name] = capacitor
        return capacitors

    @staticmethod
    def load_diode(filename):
        file = open(filename, "r")
        contents = file.readlines()
        file.close()
        param = {}
        component_name = None
        for line in contents:
            aux = line.split(": ")
            variable_name = aux[0]
            value = aux[1].split("\n")[0]
            if variable_name != "Name":
                param[variable_name] = float(value)
            else:
                component_name = value
        new_diode = Diode(param["Vd"], param["Rt"], param['Vmax'], Name=component_name)
        return [new_diode, component_name]

    def load_all_diodes(self):
        diodes = {}
        for file_path in Path("Saved Data/Components/Diodes/").glob('**/*.txt'):
            [diode, name] = self.load_diode(str(file_path))
            diodes[name] = diode
        return diodes

    @staticmethod
    def load_cable(filename):
        file = open(filename, "r")
        contents = file.readlines()
        file.close()
        param = {}
        component_name = None
        for line in contents:
            aux = line.split(": ")
            variable_name = aux[0]
            value = aux[1].split("\n")[0]
            if variable_name != "Name":
                param[variable_name] = float(value)
            else:
                component_name = value
        new_cable = Cable(param["Dcu"], param["D"], param["Rho"], param["Ur"], Name=component_name)
        return [new_cable, component_name]

    def load_all_cables(self):
        cables = {}
        for file_path in Path("Saved Data/Components/Cables/").glob('**/*.txt'):
            [cable, name] = self.load_cable(str(file_path))
            cables[name] = cable
        return cables

    @staticmethod
    def load_dissipator(filename):
        file = open(filename, "r")
        contents = file.readlines()
        file.close()
        param = {}
        component_name = None
        for line in contents:
            aux = line.split(": ")
            variable_name = aux[0]
            value = aux[1].split("\n")[0]
            if variable_name != "Name":
                param[variable_name] = float(value)
            else:
                component_name = value
        new_cable = Cable(param["Dcu"], param["D"], param["Rho"], Name=component_name)
        return [new_cable, component_name]

    def load_all_dissipators(self):
        dissipators = {}
        for filepath in Path("Saved Data/Components/Dissipators/").glob('**/*.txt'):
            [cable, name] = self.load_dissipator(str(filepath))
            dissipators[name] = cable
        return dissipators

    def load_components(self):
        cores_database = self.load_all_cores()
        cables_database = self.load_all_cables()
        switches_database = self.load_all_switches()
        capacitors_database = self.load_all_capacitors()
        diodes_database = self.load_all_diodes()
        self.database = {
            'Cores': cores_database,
            'Cables': cables_database,
            'Switches': switches_database,
            'Diodes': diodes_database,
            'Capacitors': capacitors_database
        }

    def create_available_components_maps(self):
        available_components = {
            'Capacitors': [],
            'Switches': [],
            'Cores': [],
            'Cables': [],
            'Diodes': [],
        }

        available_components_specific = {
            'C1': [],
            'C2': [],
            'C3': [],
            'C4': [],
            'D3': [],
            'D4': [],
            'S1': [],
            'S2': [],
            'Li': {
                'Core': [],
                'Cable': []
            },
            'Lk': {
                'Core': [],
                'Cable': []
            },
            'Transformer': {
                'Primary Cable': [],
                'Secondary Cable': [],
                'Core': []
            }
        }

        for name in self.database['Capacitors'].keys():
            available_components['Capacitors'].append(name)
            available_components_specific['C1'].append(name)
            available_components_specific['C2'].append(name)
            available_components_specific['C3'].append(name)
            available_components_specific['C4'].append(name)
        for name in self.database['Switches'].keys():
            available_components['Switches'].append(name)
            available_components_specific['S1'].append(name)
            available_components_specific['S2'].append(name)
        for name in self.database['Cores'].keys():
            available_components['Cores'].append(name)
            available_components_specific['Li']['Core'].append(name)
            available_components_specific['Lk']['Core'].append(name)
            available_components_specific['Transformer']['Core'].append(name)
        for name in self.database['Cables'].keys():
            available_components['Cables'].append(name)
            available_components_specific['Li']['Cable'].append(name)
            available_components_specific['Lk']['Cable'].append(name)
            available_components_specific['Transformer']['Primary Cable'].append(name)
            available_components_specific['Transformer']['Secondary Cable'].append(name)
        for name in self.database['Diodes'].keys():
            available_components['Diodes'].append(name)
            available_components_specific['D3'].append(name)
            available_components_specific['D4'].append(name)

        return available_components, available_components_specific
