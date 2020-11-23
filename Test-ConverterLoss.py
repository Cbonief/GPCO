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
converter.summarize() # Mostra um resumo do conversor criado. (Precisa de um update)



# Calcula as perdas do conversor para várias frequências, mas com a mesma indutância de entrada e 
# indutância auxiliar que a utilizada em Knaesel(2018).    
number_of_points = 100
f = np.logspace(3, 5, number_of_points)
lossVec = np.zeros(number_of_points)
t = np.zeros(number_of_points)

mean_time = 0
for n in range(0, number_of_points):
    start = time.time() 
    lossVec[n] = converter.compensated_total_loss([f[n], 2.562e-4, 1e-6], get_all=False)
    end = time.time()
    t[n] = end - start
    mean_time += t[n]
mean_time = mean_time/number_of_points

var = 0
for element in t:
    var += (element - mean_time)**2

var = np.sqrt(var)/number_of_points

print('Cada interação demorou em média {} s'.format(mean_time))
print('O desvio padrão foi de {} s'.format(var))


# Plota o gráfico da perda numa escala mono log X.
figure()



axes()
semilogx(f, lossVec)
xlabel('Frequência (Hz)')
ylabel('Perdas (W)')
grid()


show()
