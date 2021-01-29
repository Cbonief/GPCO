from Converter.BoostHalfBridge import *
from Optimizer.Numeric.Optimizer import optimize_converter
from test_components import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'


'Todos os componentes são carregados no arquivo test_components.py'

print('\nConfigurando conversor')

# Parâmetros desejáveis do conversor.
design_features = {
    'Vo': 400,
    'Vi': 17.4,
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
converter = BoostHalfBridgeInverter(design_features, safety_params, Trafo, Li, Lk, switches, diodes, capacitors)
print(Trafo)

print(converter)
[result, sucess, output] = optimize_converter(converter)

print('Solution:')
print('Fs: {} Hz'.format(output[0]))
print('Li: {} H'.format(output[1]))
print('Lk: {} H'.format(output[2]))

print(converter.compensated_total_loss(output))