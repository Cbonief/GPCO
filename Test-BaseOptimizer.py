from matplotlib.pyplot import *
import numpy as np
import time

from Converter.BoostHalfBridge import *
from TestComponents import *
from Optimizer import *


'Desenvolvido por Carlos Bonifácio Eberhardt Franco'


'Todos os componentes são carregados no arquivo TestComponents.py'

print('\nConfigurando conversor')

# Parâmetros desejáveis do conversor.
design_features = {
    'Vo': 400,
    'D': {'Nominal': 0.55, 'Max': 0.7, 'Min': 0.3},
    'Vi': {'Nominal': 17.4, 'Max': 20, 'Min': 15},
    'Ro': 1231,
    'Po': 130,
    'Bmax': {'Transformer': 0.15, 'EntranceInductor': 0.3, 'AuxiliaryInductor': 0.15},
    'dIin_max': 0.2,
    'dVo_max': 0.02,
    'dVc1': 0.10,
    'dVc2': 0.10,
    'Jmax': 450*1e4
}

# Parâmetros de segurança.
safety_params = {
    'Vc': 2.0,
    'Vd': 2.0,
    'Id': 2.0,
    'Ic': 2.0,
    'ku': {'Transformer': 0.4, 'EntranceInductor': 0.6, 'AuxiliaryInductor': 0.4}
}

# Cria uma instância do conversor Boost Half-Bridge
converter = BoostHalfBridgeInverter(Trafo, Li, Lk, design_features, switches, diodes, capacitors, safety_params)
print(converter.design_features['D'])
converter.summarize() # Mostra um resumo do conversor criado. (Precisa de um update)
print(determine_bounds(converter))
[result, sucess] = optimize_converter(converter)

output = result.x

print('Solution:')
print('Fs: {} Hz'.format(output[0]))
print('Li: {} H'.format(output[1]))
print('Lk: {} H'.format(output[2]))

print(converter.total_constraint(output))