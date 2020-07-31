from Converter.BoostHalfBridge import *
from matplotlib.pyplot import *
from Converter.Components import *
import numpy as np

'Desenvolvido por Carlos Bonifácio Eberhardt Franco'


print('\nCriando componentes')
# Cria os núcleos a serem usados.
NEE_20 = Core(0.08e-8, 0.312e-4, 0.26e-4, 1.34e-6, 7.9292e-3, 1.4017, 2.3294, 0.00923715, 0.0727958)
NEE_30_15 = Core(1.037e-8, 1.22e-4, 0.85e-4, 8.17e-6, 7.9292e-3, 1.4017, 2.3294, 0.06473752, 0.07974183)
# NEE_42_20 = Core(3.77e-8, 2.4e-4, 1.57e-4, 23.3e-6, 7.9292e-3, 1.4017, 2.3294, 23.30e-2, 0.1327705)
NEE_42_20 = Core(3.77e-8, 2.4e-4, 1.57e-4, 23.3e-6, 7.9292e-3, 1.4017, 2.3294, 0.13267917, 0.1327705)

# Cria os cabos.
rho = 56.4/1000
rho = 1.68e-8
AWG_23 = Cable(0.5753e-3, 0.5733e-3, rho, 0.999994)

# Cria as chaves.
switch1 = Switch(30e-9, 30e-9, 3e-3)
switch2 = switch1

# Cria os diodos
diode3 = Diode(1.5, 0)
diode4 = diode3

# Cria os capacitores.
capacitor1 = Capacitor(2, 31e-3 / 3)
capacitor2 = Capacitor(2, 30e-4)
capacitor3 = Capacitor(2, 550e-3)
capacitor4 = Capacitor(2, 250e-3)


diodes = [diode3, diode4]
capacitors = [capacitor1, capacitor2, capacitor3, capacitor4]
switches = [switch1, switch2]

print('\nConfigurando conversor')
# Cria as características do conversor.
# @circuit
circuit_features = {
    'Vo': 400,
    'D': {'Nominal': 0.55, 'Max': 0.7, 'Min': 0.3},
    'Vi': 17.4,
    'Ro': 1231,
    'Po': 130,
    'Bmax': {'Transformer': 0.15}
}


# Cria o conversor.
core = [NEE_30_15, NEE_42_20, NEE_20]       # Núcleos que o conversor vai usar.
cables = [AWG_23, AWG_23, AWG_23]           # Cabos que o conversor vai usar.

N = [5, 59, 28, 5]
Ncond = [8, 1, 7, 8]
Trafo = Transformer(core[0], [cables[0], cables[0]], [N[0], N[1]], [Ncond[0], Ncond[1]])
Li = Inductor(core[1], cables[1], N[2], Ncond[2])
Lk = Inductor(core[2], cables[2], N[3], Ncond[3])


converter = BoostHalfBridgeInverter(Trafo, Li, Lk, circuit_features, switches, diodes, capacitors)
Lss = 2.562e-4
uo = 4*np.pi*1e-4
lg = (28**2)*uo*NEE_42_20.Ae/Lss
f = np.linspace(800, 100e3, 1000)
lossVec = np.zeros(1000)
res1 = np.zeros(1000)
res2 = np.zeros(1000)

for n in range(0, 1000):
    lossVec[n] = converter.compensated_total_loss([f[n], Lss * 1e8, 1e10 * 1e-6])
    res = converter.total_constraint([f[n], 2 * Lss * 1e8, 1e10 * 1e-6])


figure()
axes()
semilogx(f, lossVec)
xlabel('Frequência (Hz)')
ylabel('Perdas (W)')
grid()
savefig("Saved Data/Figures/Loss_Frequency_Carolina")
#
# print('\nCalculando perdas totais')
# loss = Conversor.compensated_total_loss([50e3, 1e8*Lss, 1e10*1e-6])
# # loss = Conversor.compensated_total_loss([33184.67360181,  4602.20977969,  1716.88062291])
# print('Perdas totais = ', loss)
#
# print('\nOtimizando perdas')
# freq = Conversor.optimize()


show()