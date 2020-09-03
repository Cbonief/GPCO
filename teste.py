from Converter.BoostHalfBridge import *
from matplotlib.pyplot import *
from Converter.Components import *
import numpy as np

import time

from Optimizer import *

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'


print('\nCriando componentes')
# Cria os núcleos a serem usados.
NEE_20 = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 7.9292e-3, 1.4017, 2.3294, 0.00923715, 0.0727958)
NEE_30_15 = Core(1.037e-8, 1.22e-4, 0.85e-4, 8.17e-6, 7.9292e-3, 1.4017, 2.3294, 6.7e-2, 0.09)
NEE_42_20 = Core(3.77e-8, 2.4e-4, 1.57e-4, 23.3e-6, 7.9292e-3, 1.4017, 2.3294, 0.13267917, 0.1327705)

# Cria os cabos.
rho = 56.4/1000
rho = 1.68e-8
AWG_23 = Cable(0.5753e-3, 0.5733e-3, rho, 0.999994)

# Cria as chaves.
Coss = 370e-12
Crss = 230e-12
switch1 = Switch(30e-9, 30e-9, 3e-3, Coss-Crss)
switch2 = switch1

# Cria os diodos
diode3 = Diode(1.5, 0, 50)
diode4 = diode3

# Cria os capacitores.
capacitor1 = Capacitor(2, 31e-3 / 3, 50)
capacitor2 = Capacitor(2, 30e-4, 50)
capacitor3 = Capacitor(2, 550e-3, 400)
capacitor4 = Capacitor(2, 250e-3, 400)


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

solution = optimize_converter(converter)
print(solution)

Lss = 2.562e-4
uo = 4*np.pi*1e-7
lg = (28**2)*uo*NEE_42_20.Ae/Lss

number_of_points = 100

# f = np.logspace(3, 5, number_of_points)
# lossVec = np.zeros(number_of_points)
# t = np.zeros(number_of_points)

# last_p = 1
# mean_time = 0
# for n in range(0, number_of_points):
#     p = n
#     if p != last_p:
#         print(str(p) + "%")
#         last_p = p
#     start = time.time() 
#     lossVec[n] = converter.compensated_total_loss([f[n], Lss, 0.5e-6])
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
