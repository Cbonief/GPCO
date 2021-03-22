import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import fsolve

from Converter.auxiliary_functions import Vo_simplified, Vo, Vo_ideal
from test_components import *

'''
This test file, compares the ideal gain, the real simplified gain and 
the real gain of the Boost Half Bridge Converter.
'''

# def get_D_simplified(vo, Lk):
#     n = carolina_converter.transformer.Ratio
#     Vi = carolina_converter.features['Vi']
#     x0 = np.array([1-(n*Vi/vo)])
#     fs = 50e3
#     D = fsolve(lambda x: vo-Vo_simplified(carolina_converter, x, fs, Lk), x0)
#     return D
#
#
# vo = np.linspace(200, 1e3, 100)
#
# D05 = [get_D_simplified(v0, 0.5e-6) for v0 in vo]
# D10 = [get_D_simplified(v0, 1e-6) for v0 in vo]
# D15 = [get_D_simplified(v0, 1.5e-6) for v0 in vo]
# D20 = [get_D_simplified(v0, 2e-6) for v0 in vo]
# D25 = [get_D_simplified(v0, 2.5e-6) for v0 in vo]
#
#
# print([Vo_simplified(carolina_converter, D, 50e3, 2.5e-6) for D in D25])

duty_cycle = np.linspace(0.3, 0.7, 100)
fs = 50e3
G_ideal = [Vo_ideal(carolina_converter, D) / 17.4 for D in duty_cycle]
G_simplified05 = [Vo_simplified(carolina_converter, D, fs, 0.5e-6) / 17.4 for D in duty_cycle]
G_simplified10 = [Vo_simplified(carolina_converter, D, fs, 1e-6) / 17.4 for D in duty_cycle]
G_simplified30 = [Vo_simplified(carolina_converter, D, fs, 1.0e-5) / 17.4 for D in duty_cycle]
G05 = [Vo(carolina_converter, D, fs, 0.5e-6) / 17.4 for D in duty_cycle]
G10 = [Vo(carolina_converter, D, fs, 1e-6) / 17.4 for D in duty_cycle]
G30 = [Vo(carolina_converter, D, fs, 1.0e-5) / 17.4 for D in duty_cycle]

plt.figure()
plt.axes()
plt.plot(duty_cycle, G_ideal, label='Ganho Ideal')
plt.plot(duty_cycle, G_simplified05, '--', label=r'Ganho Simplificado $L_{k}=0.5 \mu H$')
plt.plot(duty_cycle, G05, label=r'Ganho Real $L_{k}=0.5 \mu H$')
plt.plot(duty_cycle, G_simplified30, '--', label=r'Ganho Simplificado $L_{k}=10 \mu H$')
plt.plot(duty_cycle, G30, label=r'Ganho Real $L_{k}=10 \mu H$')
plt.xlabel("D", fontsize=12)
plt.ylabel("Ganho", fontsize=12)
plt.xlim([0.3, 0.7])
plt.grid()
plt.legend()

plt.show()
