from Converter.BoostHalfBridge import *
from matplotlib.pyplot import *
from Converter.Components import *
import numpy as np

import time

from Optimizer import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'

print('\nCriando componentes')
# Cria os núcleos a serem usados.
NEE_20 = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 7.9292e-3, 1.4017, 2.3294, 3.8e-2, 11e-3, Name = 'NEE_20')                 # Lk
NEE_30_15 = Core(1.037e-8, 1.22e-4, 0.85e-4, 8.17e-6, 7.9292e-3, 1.4017, 2.3294, 6.7e-2, 17.2e-3, Name = 'NEE_30_15')         # Trafo
NEE_42_20 = Core(3.77e-8, 2.4e-4, 1.57e-4, 23.3e-6, 7.9292e-3, 1.4017, 2.3294, 8.7e-2, 25.9e-3, Name = 'NEE_42_20')           # Li

# Cria os cabos.
AWG_23 = Cable(0.5753e-3, 0.5733e-3, 1.68e-8, 0.999994, Name = 'AWG_23')

# Cria as chaves.
IRFR7740PbF = Switch(30e-9, 30e-9, 3e-3, 75, 140e-12, Name='IRFR7740PbF')
switch1 = IRFR7740PbF
switch2 = switch1

# Cria os diodos
HFA04SD60S = Diode(1.5, 0, 620, Name='HFA04SD60S')
diode3 = HFA04SD60S
diode4 = HFA04SD60S

# Cria os capacitores.
capacitor1 = Capacitor(2, 31e-3 / 3, 55, Name='C1')
capacitor2 = Capacitor(2, 30e-4, 55, Name='C2')
capacitor3 = Capacitor(2, 550e-3, 450, Name='C3')
capacitor4 = Capacitor(2, 250e-3, 450, Name='C4')


diodes = [diode3, diode4]
capacitors = [capacitor1, capacitor2, capacitor3, capacitor4]
switches = [switch1, switch2]

print('\nConfigurando conversor')
# Cria as características do conversor.
# @circuit
circuit_features = {
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

safety_params = {
    'Vc': 2.0,
    'Vd': 2.0,
    'Id': 2.0,
    'Ic': 2.0,
    'ku': {'Transformer': 0.4, 'EntranceInductor': 0.6, 'AuxiliaryInductor': 0.4}
}


# Cria o conversor.
core = [NEE_30_15, NEE_42_20, NEE_20]       # Núcleos que o conversor vai usar.
cables = [AWG_23, AWG_23, AWG_23]           # Cabos que o conversor vai usar.

N = [5, 59, 28, 5]
Ncond = [8, 1, 7, 8]
Trafo = Transformer(core[0], [cables[0], cables[0]], [N[0], N[1]], [Ncond[0], Ncond[1]])
Li = Inductor(core[1], cables[1], N[2], Ncond[2])
Lk = Inductor(core[2], cables[2], N[3], Ncond[3])

converter = BoostHalfBridgeInverter(Trafo, Li, Lk, circuit_features, switches, diodes, capacitors, safety_params)
converter.summarize()

solution = optimize_converter(converter, epochs=10)
print(solution)
# constraints = converter.total_constraint(solution.x)
# print(constraints)
    
Lss = 2.562e-4
uo = 4*np.pi*1e-7
lg = (28**2)*uo*NEE_42_20.Ae/Lss

number_of_points = 100

f = np.logspace(3, 5, number_of_points)
lossVec = np.zeros(number_of_points)
t = np.zeros(number_of_points)

expected_losses = {
    'Transformer': {'Core': 2.911, 'Primary': 0.718, 'Secondary': 0.82},
    'EntranceInductor': {'Core': 0.036, 'Cable': 2.103},
    'AuxiliaryInductor': {'Core': 0.438, 'Cable': 0.235},
    'Capacitors': {'C1': 0.148, 'C2': 0.181, 'C3': 0.112, 'C4': 0.038},
    'Diode': {'D3': 0.487, 'D4': 0.487},
    'Switches': {'S1': 0.308, 'S2': 0.957}
}
total = 0
for component in expected_losses:
    for lossType in expected_losses[component]:
        total += expected_losses[component][lossType]
expected_losses['Total'] = total

losses = converter.compensated_total_loss([50e3, Lss, 1e-6], get_all=True)
error = {}
for component in expected_losses:
    error[component] = {}
    if component != 'Total':
        for lossType in expected_losses[component]:
            expected = expected_losses[component][lossType]
            calculated = losses[component][lossType]
            error[component][lossType] = round(100*(expected - calculated)/expected)
    else:
        error[component] = round(100*(expected_losses[component] - losses[component])/expected_losses[component])


Bmax = Lss * 7.836 / (converter.entrance_inductor.Core.Ae * converter.entrance_inductor.N)
dB = Lss * 0.747 / (converter.entrance_inductor.Core.Ae * converter.entrance_inductor.N)

expected_values = {
    'Vc3': 218.297,
    'Vc4': 181.496,
    'D': 0.55,'t3': 4.374e-7, 't6': 1.136e-5,
    'Vc1': 21.267, 'Vc2': 17.4,
    'Ipk_pos': 16.239, 'Ipk_neg': -13.286, 'Ipk_pos_1': 16.096, 'Ipk_neg_1': -13.383,
    'Ipk': 7.836, 'Imin': 7.089,'Iin': 7.462,'dIin': 0.747,
    'dBLi': dB, 'BmaxLi': Bmax,
    'Is1max': 9.15,'Is2max': 21.112,
    'TransformerIrms': 8.474,
    'C1Irms': 3.789,'C2Irms': 7.759,
    'S1Irms': 3.789,'S2Irms': 10.715,
    'D3Iavg': 0.325,'D3Irms': 0.557,
    'D4Iavg': 0.325,'D4Irms': 0.508,
    'C3Irms': 0.452, 'C4Irms': 0.38
}

# simulation_error = {}
# for value in expected_values:
#     expected = expected_values[value]
#     calculated = converter.calculated_values[value]
#     simulation_error[value] = round(100*(expected - calculated)/expected,2)

# print('Erro das Perdas (> 20 %)')
# for component in error:
#     if component != 'Total':
#         for lossType in error[component]:
#             if abs(error[component][lossType]) > 10:
#                 print('Perdas: '+component+'/'+lossType +': '+str(error[component][lossType])+' %')

# print('Erro da Simulação (> 20%)')
# for var in simulation_error:
#     if abs(simulation_error[var]) > 10:
#         print('Erro' + var + ':' + str(simulation_error[var])+' %')


# last_p = 1
# mean_time = 0
# for n in range(0, number_of_points):
#     p = n
#     if p != last_p:
#         print(str(p) + "%")
#         last_p = p
#     start = time.time() 
#     lossVec[n] = converter.compensated_total_loss([f[n], Lss, 0.5e-6], get_all=True)
#     end = time.time()
#     t[n] = end - start
#     mean_time += t[n]
# mean_time = mean_time/100
# print(mean_time)

# var = 0
# for element in t:
#     var += (element - mean_time)**2

# var = np.sqrt(var)/100
# print(var)
    
# for lossClass in Losses:
#     print(lossClass)
#     printString1 = ""
#     printString2 = ""
#     if lossClass != "Total":
#         for lossType in Losses[lossClass]:
#             printString1 += lossType + " | "
#             printString2 += str(Losses[lossClass][lossType]) + " | "
#     print(printString1)
#     print(printString2)

# minimo = 100
# bestF = 0
# for [freq, loss] in zip(f, lossVec):
#     if loss < minimo:
#         minimo = loss
#         bestF = freq


# print(bestF)

# print(determine_bounds(converter))

# figure()
# axes()
# semilogx(f, lossVec)
# xlabel('Frequência (Hz)')
# ylabel('Perdas (W)')
# grid()
# savefig("Saved Data/Figures/Loss_Frequency_Carolina")
# show()
