from Optimizer import *
from TestComponents import *



'Desenvolvido por Carlos Bonifácio Eberhardt Franco'

print('\nCriando componentes')

diodes = [HFA04SD60S, IdealDiode]
capacitors = [capacitor1, capacitor2, capacitor3, capacitor4]
switches = [IRFR7740PbF, IdealSwitch]
cores = [NEE_20, NEE_30_15, NEE_42_20_Ideal, NEE_20_Ideal, NEE_30_15_Ideal, NEE_42_20_Ideal]
cables = [AWG_23, IdealCable]

selected_components = {
    'Cores': cores,
    'Switches': switches,
    'Capacitors': capacitors,
    'Diodes': diodes,
    'Cables': cables
}

print('\nConfigurando conversor')
# Cria as características do conversor.
# @circuit
design_features = {
    'Vo': 400,
    'D': {'Max': 0.7, 'Min': 0.3},
    'Vi': {'Nominal': 17.4, 'Max': 25, 'Min': 15},
    'Ro': 1231,
    'Po': 130,
    'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15},
    'dIin_max': 0.2,
    'dVo_max': 0.02,
    'dVc1': 0.02,
    'dVc2': 0.02,
    'Jmax': 450*1e4
}

safety_params = {
    'Vc': 1.5,
    'Vd': 1.5,
    'Id': 2.0,
    'Ic': 2.0,
    'Vs': 1.75,
    'Is': 2.0,
    'ku': {'Transformer': 0.4, 'EntranceInductor': 0.6, 'AuxiliaryInductor': 0.4}
}

GA = genetic_optimizer(selected_components, design_features, safety_params)
sol = GA.optimize(population_size=10)