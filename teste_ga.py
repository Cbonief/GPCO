from Converter.BoostHalfBridge import *
from matplotlib.pyplot import *
from Converter.Components import *
import numpy as np
import FileHandler as fh

import time

from Optimizer import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'

print('\nCriando componentes')
# Cria os núcleos a serem usados.
NEE_20 = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 7.9292e-3, 1.4017, 2.3294, 3.8e-2, 11e-3, Name = 'NEE_20')                 # Lk
NEE_30_15 = Core(1.037e-8, 1.22e-4, 0.85e-4, 8.17e-6, 7.9292e-3, 1.4017, 2.3294, 6.7e-2, 17.2e-3, Name = 'NEE_30_15')         # Trafo
NEE_42_20 = Core(3.77e-8, 2.4e-4, 1.57e-4, 23.3e-6, 7.9292e-3, 1.4017, 2.3294, 8.7e-2, 25.9e-3, Name = 'NEE_42_20')           # Li
NEE_20_Ideal = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 0, 1.4017, 2.3294, 3.8e-2, 11e-3, Name = 'NEE_20')                 # Lk
NEE_30_15_Ideal = Core(1.037e-8, 1.22e-4, 0.85e-4, 8.17e-6, 0, 1.4017, 2.3294, 6.7e-2, 17.2e-3, Name = 'NEE_30_15')         # Trafo
NEE_42_20_Ideal = Core(3.77e-8, 2.4e-4, 1.57e-4, 23.3e-6, 0, 1.4017, 2.3294, 8.7e-2, 25.9e-3, Name = 'NEE_42_20')           # Li

# Cria os cabos.
AWG_23 = Cable(0.5753e-3, 0.5733e-3, 1.68e-8, 0.999994, Name = 'AWG_23')
IdealCable = Cable(0.5753e-3, 0.5733e-3, 1e-12, 0.999994, Name = 'IdealCable')

# Cria as chaves.
IRFR7740PbF = Switch(30e-9, 30e-9, 3e-3, 75,140e-12, Name='IRFR7740PbF')
IdealSwitch = Switch(0, 0, 0, 75, 140e-12, Name='IdealSwitch')

# Cria os diodos
HFA04SD60S = Diode(1.5, 0, 620, Name='HFA04SD60S')
IdealDiode = Diode(0.5, 0, 620, Name='IdealDiode')

# Cria os capacitores.
capacitor1 = Capacitor(2, 31e-3 / 3, 55, Name='C1')
capacitor2 = Capacitor(2, 30e-4, 55, Name='C2')
capacitor3 = Capacitor(2, 550e-3, 450, Name='C3')
capacitor4 = Capacitor(2, 250e-3, 450, Name='C4')


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