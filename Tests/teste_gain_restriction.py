# Arquivo de teste para as novas restrições de Lk e Fs baseadas na equação do ganho.

from Converter.BoostHalfBridge import *
from Converter.Restrictions import *
from Converter.auxiliary_functions import vc3_vc4_d
from test_components import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'


'Todos os componentes são carregados no arquivo test_components.py'

print('\nConfigurando conversor')

# Parâmetros desejáveis do conversor.
design_features = {
    'Vo': 400,
    'D': {'Nominal': 0.55, 'Max': 0.7, 'Min': 0.3},
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


# Calcula as perdas do conversor para várias frequências, mas com a mesma indutância de entrada e 
# indutância auxiliar que a utilizada em Knaesel(2018).    
number_of_points = 100
Freq = np.logspace(3, 5, number_of_points)
Aux = np.logspace(-7, -5, number_of_points)

for fs in Freq:
	for Lk in Aux:
		[x,y,z], feasible = vc3_vc4_d(converter, fs, Lk)
		guess = gain_restriction_feasible(converter, [fs, 2.562e-4, Lk])
		if (guess and not feasible):
			print('Found Mismatch at point [{}, {}] not feasible'.format(round(fs,2),round(Lk,10)))
		if (not guess and feasible):
			print('Found Mismatch at point [{}, {}] not guessed'.format(round(fs,2),round(Lk,10)))
			print(gain_restriction(converter, [fs, 2.562e-4, Lk]))