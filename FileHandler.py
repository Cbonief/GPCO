from Converter.Components import *
from pathlib import Path


# Done
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
    new_core = Core(param["AeAw"], param["Ae"], param["Aw"], param["Ve"], param["Alpha"], param["Beta"], param["Kc"], param["Lt"], 2)
    return [new_core, core_name]


# Done
def load_all_cores():
    Cores = {}
    for file_path in Path("Saved Data/Components/Cores/").glob('**/*.txt'):
        [core, name] = load_core(str(file_path))
        Cores[name] = core
    return Cores


# Done
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
    new_switch = Switch(param["Ton"], param["Toff"], param["Rd"], param['Cds'])
    return [new_switch, component_name]


# Done
def load_all_switches():
    Switches = {}
    for file_path in Path("Saved Data/Components/Switches/").glob('**/*.txt'):
        [switch, name] = load_switch(str(file_path))
        Switches[name] = switch
    return Switches


# Done
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
    new_capacitor = Capacitor(param["C"], param["Rse"], param['Vmax'])
    return [new_capacitor, component_name]


# Done
def load_all_capacitors():
    Capacitors = {}
    for file_path in Path("Saved Data/Components/Capacitors/").glob('**/*.txt'):
        [capacitor, name] = load_capacitor(str(file_path))
        Capacitors[name] = capacitor
    return Capacitors


# Done
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
    new_diode = Diode(param["Vd"], param["Rt"], param['Vmax'])
    return [new_diode, component_name]


# Done
def load_all_diodes():
    Diodes = {}
    for file_path in Path("Saved Data/Components/Diodes/").glob('**/*.txt'):
        [diode, name] = load_diode(str(file_path))
        Diodes[name] = diode
    return Diodes


# Done
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
    new_cable = Cable(param["Dcu"], param["D"], param["Rho"], 1)
    return [new_cable, component_name]


# Done
def load_all_cables():
    Cables = {}
    for file_path in Path("Saved Data/Components/Cables/").glob('**/*.txt'):
        [cable, name] = load_cable(str(file_path))
        Cables[name] = cable
    return Cables


# Done
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
    new_cable = Cable(param["Dcu"], param["D"], param["Rho"])
    return [new_cable, component_name]


# Done
def load_all_dissipators():
    Cables = {}
    for filepath in Path("Saved Data/Components/Dissipators/").glob('**/*.txt'):
        [cable, name] = load_dissipator(str(filepath))
        Cables[name] = cable
    return Cables
