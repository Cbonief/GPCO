from Optimizer.GeneticAlgorithm.CustomUtilization import optimize_components
from test_components import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'

print('Running test_genetic_algorithm.py')

# Carrega os componentes presentes no arquivo test_components.py.
diodes = [HFA04SD60S, IdealDiode]
diode_map = {}
for diode in diodes:
    diode_map[diode.get_name()] = diode
capacitors = [capacitor1, capacitor2, capacitor3, capacitor4]
capacitor_map = {}
for capacitor in capacitors:
    capacitor_map[capacitor.get_name()] = capacitor
switches = [IRFR7740PbF, IdealSwitch]
switch_map = {}
for switch in switches:
    switch_map[switch.get_name()] = switch
cores = [NEE_20, NEE_30_15, NEE_42_20_Ideal, NEE_20_Ideal, NEE_30_15_Ideal, NEE_42_20_Ideal]
core_map = {}
for core in cores:
    core_map[core.get_name()] = core
cables = [AWG_23, IdealCable]
cable_map = {}
for cable in cables:
    cable_map[cable.get_name()] = cable

# Cria a estura responsável por passar os componentes disponível para a busca do Optimizer.
components_data_base = {
    'Cores': core_map,
    'Switches': switch_map,
    'Capacitors': capacitor_map,
    'Diodes': diode_map,
    'Cables': cable_map
}

selected_components_keys = {}
for key in components_data_base.keys():
    selected_components_keys[key] = []
    for component_name in components_data_base[key].keys():
        selected_components_keys[key].append(component_name)

# Parâmetros desejáveis do conversor.
design_features = {
    'Vo': 400,
    'D': {'Max': 0.7, 'Min': 0.3},
    'Vi': 17.4,
    'Ro': 1231,
    'Po': 130,
    'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15},
    'dIin_max': 0.2,
    'dVo_max': 0.02,
    'dVc1': 0.02,
    'dVc2': 0.02,
    'Jmax': 450*1e4
}

# Parâmetros de segurança.
safety_parameters = {
    'Vc': 1.5,
    'Vd': 1.5,
    'Id': 2.0,
    'Ic': 2.0,
    'Vs': 1.2,
    'Is': 2.0,
    'ku': {'Transformer': 0.4, 'EntranceInductor': 0.6, 'AuxiliaryInductor': 0.4}
}

converter = optimize_components(selected_components_keys, components_data_base, design_features, safety_parameters)
print(converter)
