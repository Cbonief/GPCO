from Components import *
from pathlib import Path

# Done
def loadCore(filename):
    file = open(filename, "r")
    contents = file.readlines()
    file.close()
    param = {}
    core_name = None
    for line in contents:
        aux = line.split(": ")
        variable_name = aux[0]
        value = aux[1].split("\\n")[0]
        if variable_name != "Name":
            param[variable_name] = float(value)
        else:
            core_name = value
    new_core = Core(param["AeAw"], param["Ae"], param["Aw"], param["Ve"], param["Alpha"], param["Beta"], param["Kc"], param["Lt"])
    return [new_core, core_name]

# Done
def loadCores():
    Cores = {}
    for filepath in Path("Components/Cores/").glob('**/*.txt'):
        [core, name] = loadCore(str(filepath))
        Cores[name] = core
    return Cores

# Done
def loadSwitch(filename):
    file = open(filename, "r")
    contents = file.readlines()
    file.close()
    param = {}
    component_name = None
    for line in contents:
        aux = line.split(": ")
        variable_name = aux[0]
        value = aux[1].split("\\n")[0]
        if variable_name != "Name":
            param[variable_name] = float(value)
        else:
            component_name = value
    new_switch = Switch(param["Ton"], param["Toff"], param["Rd"])
    return [new_switch, component_name]

# Done
def loadSwitches():
    Switches = {}
    for filepath in Path("Components/Switches/").glob('**/*.txt'):
        [switch, name] = loadSwitch(str(filepath))
        Switches[name] = switch
    return Switches

# Done
def loadCapacitor(filename):
    file = open(filename, "r")
    contents = file.readlines()
    file.close()
    param = {}
    component_name = None
    for line in contents:
        aux = line.split(": ")
        variable_name = aux[0]
        value = aux[1].split("\\n")[0]
        if variable_name != "Name":
            param[variable_name] = float(value)
        else:
            component_name = value
    new_capacitor = Capacitor(param["C"], param["Rse"])
    return [new_capacitor, component_name]

# Done
def loadCapacitors():
    Capacitors = {}
    for filepath in Path("Components/Capacitors/").glob('**/*.txt'):
        [capacitor, name] = loadCapacitor(str(filepath))
        Capacitors[name] = capacitor
    return Capacitors

# Done
def loadDiode(filename):
    file = open(filename, "r")
    contents = file.readlines()
    file.close()
    param = {}
    component_name = None
    for line in contents:
        aux = line.split(": ")
        variable_name = aux[0]
        value = aux[1].split("\\n")[0]
        if variable_name != "Name":
            param[variable_name] = float(value)
        else:
            component_name = value
    new_diode = Diode(param["Vd"], param["Rt"])
    return [new_diode, component_name]

# Done
def loadDiodes():
    Diodes = {}
    for filepath in Path("Components/Diodes/").glob('**/*.txt'):
        [diode, name] = loadDiode(str(filepath))
        Diodes[name] = diode
    return Diodes

# Done
def loadCable(filename):
    file = open(filename, "r")
    contents = file.readlines()
    file.close()
    param = {}
    component_name = None
    for line in contents:
        aux = line.split(": ")
        variable_name = aux[0]
        value = aux[1].split("\\n")[0]
        if variable_name != "Name":
            param[variable_name] = float(value)
        else:
            component_name = value
    new_cable = Cable(param["Dcu"], param["D"], param["Rho"])
    return [new_cable, component_name]

# Done
def loadCables():
    Cables = {}
    for filepath in Path("Components/Cables/").glob('**/*.txt'):
        [cable, name] = loadCable(str(filepath))
        Cables[name] = cable
    return Cables

# Done
def loadDissipator(filename):
    file = open(filename, "r")
    contents = file.readlines()
    file.close()
    param = {}
    component_name = None
    for line in contents:
        aux = line.split(": ")
        variable_name = aux[0]
        value = aux[1].split("\\n")[0]
        if variable_name != "Name":
            param[variable_name] = float(value)
        else:
            component_name = value
    new_cable = Cable(param["Dcu"], param["D"], param["Rho"])
    return [new_cable, component_name]

# Done
def loadDissipators():
    Cables = {}
    for filepath in Path("Components/Cables/").glob('**/*.txt'):
        [cable, name] = loadCable(str(filepath))
        Cables[name] = cable
    return Cables

def loadFSD():
    file = open("FSD/FSD_data.txt", "r")
    contents = file.readlines()
    file.close()
    fsd = []
    for line in contents:
        aux = line.split("\t")
        aux2 = aux[1].split("\n")
        fsd.append(float(aux2[0]))
    return tuple(fsd)